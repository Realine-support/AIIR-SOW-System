"""
Cleanup Test Documents
Deletes all test documents from the Client Documents folder
"""

from app.services.google_drive import GoogleDriveService
from app.config import get_config

def cleanup_test_documents():
    config = get_config()
    drive = GoogleDriveService(config.google_credentials_path)

    print("Fetching all files in Client Documents folder...")
    files = drive.list_files_in_folder(config.client_documents_folder_id)

    if not files:
        print("No files found to delete")
        return

    print(f"Found {len(files)} file(s) to delete:\n")

    for file in files:
        file_name = file.get('name', 'Unknown')
        file_id = file.get('id')
        mime_type = file.get('mimeType', '')

        print(f"  - {file_name} ({mime_type})")

        # Delete the file
        try:
            drive.delete_file(file_id)
            print(f"    DELETED")
        except Exception as e:
            print(f"    ERROR: {e}")

    print(f"\nCleanup complete! Deleted {len(files)} file(s)")

if __name__ == '__main__':
    cleanup_test_documents()
