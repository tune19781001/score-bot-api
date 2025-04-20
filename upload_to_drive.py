import os
import mimetypes
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ✅ 外部から呼び出せるアップロード関数を定義

def upload_file_to_drive(file_path, credentials_file="credentials.json", token_file="token.json"):
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": os.path.basename(file_path)}
    media_mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    media = MediaFileUpload(file_path, mimetype=media_mime, resumable=True)

    # 既存ファイル検索
    results = service.files().list(q=f"name='{os.path.basename(file_path)}'", spaces='drive').execute()
    files = results.get('files', [])

    if files:
        # 上書き
        file_id = files[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"🔄 {file_path} をGoogle Drive上で上書きしました。")
    else:
        # 新規アップロード
        service.files().create(body=file_metadata, media_body=media).execute()
        print(f"✅ {file_path} をGoogle Driveに新規アップロードしました。")

# スクリプトとして実行されたときのみアップロードを行う
if __name__ == "__main__":
    upload_file_to_drive("conversation_history.json")
