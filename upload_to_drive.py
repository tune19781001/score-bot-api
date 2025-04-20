import os
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload  # ← ✅ これが追加された部分！

# アップロード対象のファイル名
TARGET_FILE = "conversation_history.json"

# Google Drive API のスコープ
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# 最初の認証フロー（トークン保存）
def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# Driveにファイルアップロード（同名ファイルがあれば上書き）
def upload_to_drive():
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": TARGET_FILE}
    media_mime = mimetypes.guess_type(TARGET_FILE)[0] or "application/octet-stream"

    media = MediaFileUpload(TARGET_FILE, mimetype=media_mime, resumable=True)
    results = service.files().list(q=f"name='{TARGET_FILE}'", spaces='drive').execute()
    files = results.get('files', [])

    if files:
        # 上書き
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print("🔄 Google Drive 上でファイルを上書きしました。")
    else:
        # 新規アップロード
        service.files().create(body=file_metadata, media_body=media).execute()
        print("✅ Google Drive に新しくアップロードしました。")

# スクリプトを直接実行した場合のみアップロード実行
if __name__ == "__main__":
    upload_to_drive()
