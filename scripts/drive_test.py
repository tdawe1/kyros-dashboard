#!/usr/bin/env python3
"""
Quick sanity check that your Google Drive Service Account can read your Plans Inbox.
Usage:
  python3 scripts/drive_test.py --key service-account.json --folder <FOLDER_ID>
Or with env vars:
  GDRIVE_SA_JSON_PATH=service-account.json PLANS_INBOX_FOLDER_ID=<FOLDER_ID> python3 scripts/drive_test.py
"""
import os, io, json, argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from retry_utils import retry_with_backoff

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("GDRIVE_SA_JSON_PATH"), help="Path to service account JSON")
    ap.add_argument("--folder", default=os.environ.get("PLANS_INBOX_FOLDER_ID"), help="Drive Folder ID (Plans Inbox)")
    args = ap.parse_args()

    if not args.key or not os.path.exists(args.key):
        raise SystemExit("Missing --key file (service account JSON). Set GDRIVE_SA_JSON_PATH or pass --key.")

    if not args.folder:
        raise SystemExit("Missing --folder (Drive Folder ID). Set PLANS_INBOX_FOLDER_ID or pass --folder.")

    with open(args.key, "r", encoding="utf-8") as f:
        sa = json.load(f)

    creds = service_account.Credentials.from_service_account_info(
        sa, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    svc = build("drive", "v3", credentials=creds)

    # list newest .yml in the folder with retry
    resp = retry_with_backoff(
        svc.files().list,
        max_retries=3,
        q=f"'{args.folder}' in parents and trashed=false and name contains '.yml'",
        orderBy="modifiedTime desc",
        pageSize=5,
        fields="files(id,name,modifiedTime)"
    ).execute()
    
    files = resp.get("files", [])
    if not files:
        raise SystemExit("No *.yml files found. Make sure the SA EMAIL has at least Viewer on the folder, and a PlanSpec is there.")

    print("Newest plan files:")
    for f in files:
        print(f" - {f['name']}  ({f['modifiedTime']})  id={f['id']}")

    # download latest with retry
    fid, name = files[0]["id"], files[0]["name"]
    req = svc.files().get_media(fileId=fid)
    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, req)
    
    def download_chunks():
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buf.getvalue()
    
    file_data = retry_with_backoff(download_chunks, max_retries=3)
    
    out = "planspec.yml"
    with open(out, "wb") as w:
        w.write(file_data)
    print(f"Downloaded {name} → ./{out}")

if __name__ == "__main__":
    main()
