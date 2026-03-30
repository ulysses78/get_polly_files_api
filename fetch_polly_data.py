#from dotenv import load_dotenv
import os
import requests
import argparse
from pathlib import Path
import json


# --- Argument parser ---
parser = argparse.ArgumentParser(description="Download files for a given site/date")
parser.add_argument("--site", required=True, help="Site name, e.g. leipzig, melpitz, mindelo, dushanbe, limassol, invercargill ...")
parser.add_argument("--date", required=True, help="Date in YYYYMMDD")
parser.add_argument("--api-key",  required=True, help="Use specific API key")
parser.add_argument("--download", action="store_true", help="Switch for downloading or just showing the results")
parser.add_argument("--download_dir", default=".", help="The folder to download to. Only necessary if download switch is activated")
args = parser.parse_args()



# --- Configuration ---
BASE_URL = "https://rsd2.tropos.de/polly_api"
API_KEY = args.api_key


headers = {"X-API-Key": API_KEY}
params = {"site": args.site, "date": args.date}


# --- Make API request ---
api_url = f"{BASE_URL}/api?"
response = requests.get(api_url, headers=headers, params=params)
try:
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    print("HTTP error:", e)

data = response.json()

if not args.download:
    print(json.dumps(data, indent=4))
    exit(1)
else:
    print(json.dumps(data, indent=4))
    api_download_url =  f"{BASE_URL}/apitoken?"
    response = requests.get(api_download_url, headers=headers, params=params)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("HTTP error:", e)
    data_tokens = response.json()
    print('downloading... ')
    if data_tokens:
        if 'download_tokens' in data_tokens.keys():
            for token in data_tokens['download_tokens']:
                download_url = f"{BASE_URL}/download/{token}"
                with requests.get(download_url, stream=True, timeout=300) as r:
                        r.raise_for_status()
                
                        filename = None
                        cd = r.headers.get("Content-Disposition")
                        if cd and "filename=" in cd:
                            filename = cd.split("filename=")[-1].strip('"')
                
                        if not filename:
                            filename = "downloaded_file"
                
                        out_path = os.path.join(args.download_dir, filename)
                        print(filename)

                        with open(out_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=1024 * 1024):
                                if chunk:
                                    f.write(chunk)
            print('Download complete.')
        else:
            print('no tokens available')
    else:
        print('no tokens available')


