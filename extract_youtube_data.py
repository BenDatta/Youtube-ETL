import requests
import os
from dotenv import load_dotenv
import json
from datetime import date
from pathlib import Path


load_dotenv()
maxResult = 50
channel_handle = "MrBeast"
API_KEY = os.getenv("YOUTUBE_API_KEY")

folder_path = Path(__file__).parent / "data"
file_path = folder_path / f"youtube_data_{date.today()}.json"


def get_channel_id():

    try:
        youtube_url = (
            f"https://youtube.googleapis.com/youtube/v3/channels?"
            f"part=contentDetails&forHandle={channel_handle}&key={API_KEY}"
        )

        response = requests.get(youtube_url)

        response.raise_for_status()

        data = response.json()

        channel_items = data["items"][0]

        playlist_id = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]

        print(playlist_id)

        return playlist_id
    except requests.exceptions.RequestException as e:
        raise e


def get_video_ids(playlist_id):
    video_ids = []
    page_token = None

    try:
        while True:
            url = (
                f"https://youtube.googleapis.com/youtube/v3/playlistItems"
                f"?part=contentDetails&playlistId={playlist_id}"
                f"&maxResults={maxResult}&key={API_KEY}"
            )
            if page_token:
                url += f"&pageToken={page_token}"

            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            page_token = data.get("nextPageToken")
            if not page_token:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e


def extracted_video_data(video_ids):

    extracted_data = []

    def batch_list(video_ids_list, batch_size):
        for video_id in range(0, len(video_ids_list), batch_size):
            yield video_ids_list[video_id : video_id + batch_size]

    try:
        for batch in batch_list(video_ids, maxResult):
            video_id_str = ",".join(batch)

            base_url = (
                f"https://youtube.googleapis.com/youtube/v3/videos?"
                f"part=contentDetails&part=snippet&part=statistics&id={video_id_str}"
                f"&key={API_KEY}"
            )
            response = requests.get(base_url)

            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "published_at": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "view_count": statistics.get("viewCount", None),
                    "like_count": statistics.get("likeCount", None),
                    "comment_count": statistics.get("commentCount", None),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    playlist_id = get_channel_id()
    video_ids = get_video_ids(playlist_id)
    video_data = extracted_video_data(video_ids)
    save_to_json(video_data)
