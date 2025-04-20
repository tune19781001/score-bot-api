import os
import mimetypes
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_file_to_drive(file_path):
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    # ✅ サービスアカウントで認証
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )

    # ✅ Driveにアップロード
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": os.path.basename(file_path)}
    media_mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    media = MediaFileUpload(file_path, mimetype=media_mime, resumable=True)

    results = service.files().list(q=f"name='{os.path.basename(file_path)}'", spaces='drive').execute()
    files = results.get('files', [])

    if files:
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"🔄 {file_path} をGoogle Drive上で上書きしました。")
    else:
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"✅ {file_path} をGoogle Driveに新規アップロードしました。")

# テスト実行（任意）
if __name__ == "__main__":
    upload_file_to_drive("conversation_history.json")

