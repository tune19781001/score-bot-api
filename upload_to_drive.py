import os
import mimetypes
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_file_to_drive(file_path, credentials_file="credentials.json", token_file="token.json"):
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]
    creds = None

    # ✅ credentials.json の代わりに環境変数から読み込み
    if "GOOGLE_CREDENTIALS_JSON" in os.environ:
        credentials_data = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
        flow = InstalledAppFlow.from_client_config(credentials_data, SCOPES)
    elif os.path.exists(credentials_file):
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    else:
        raise FileNotFoundError("Google認証情報が見つかりません（credentials.json または GOOGLE_CREDENTIALS_JSON）")

    # ✅ 認証トークン処理
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())

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

# スクリプト単体実行用（任意）
if __name__ == "__main__":
    upload_file_to_drive("conversation_history.json")
