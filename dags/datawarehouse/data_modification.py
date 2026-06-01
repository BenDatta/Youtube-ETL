# Alias for typo-tolerant imports (module file is data_modifications.py)
from datawarehouse.data_modifications import delete_rows, insert_rows, update_rows

__all__ = ["insert_rows", "update_rows", "delete_rows"]
