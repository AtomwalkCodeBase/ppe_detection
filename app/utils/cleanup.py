import os
from datetime import datetime, timedelta

SNAPSHOT_BASE_DIR = "app/storage/snapshots"
RETENTION_DAYS = 3 

def cleanup_old_snapshots():
    if not os.path.exists(SNAPSHOT_BASE_DIR):
        print("Snapshot directory does not exist")
        return

    cutoff_time = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_files = 0

    for root, dirs, files in os.walk(SNAPSHOT_BASE_DIR):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    deleted_files += 1

            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    print(f"Cleanup complete. Deleted {deleted_files} old snapshot files.")
