import os
import sys
import toml
import json
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Query, Security
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED
from urllib.parse import unquote
from typing import Optional
#from dotenv import load_dotenv
from typing import Optional, Dict, List
from itsdangerous import URLSafeTimedSerializer, SignatureExpired  ## for one-time-token-generation with encrypted api-download-filename
import api_helper as helper
import tromeda.tromeda_functions as tromeda
#load_dotenv()

#API_KEYS = set(os.getenv("API_KEYS", "").split(","))

app = FastAPI()

config_file = "/lacroshome/cloudnetpy/src/get_polly_data/api_config_file.json"
tromeda_config_file = "/lacroshome/lacroswww/src/quicklooks/tromeda_config.json"

####
with open(tromeda_config_file,"r") as tromeda_con_file:
                tromeda_config_dict = json.load(tromeda_con_file)
pylarda_basedir = tromeda_config_dict['pylarda_basedir']

with open(config_file,"r") as con_file:
    con = json.load(con_file)
    md_file = con['dev_md_file']  ## import md file

API_KEY_MAP: Dict[str, List[str]] = con["api_keys"]

# Secret key used to sign tokens (keep private!)
SECRET_KEY = con["api_token_generation_key"]
# Token expiration in seconds (e.g., 5 minutes)
TOKEN_MAX_AGE = 60

serializer = URLSafeTimedSerializer(SECRET_KEY)

def create_download_token(filename: str, site: str) -> str:
    """Create a signed token containing filename and site"""
    payload = {"filename": str(filename), "site": site}
    return serializer.dumps(payload, salt="download-token")

def verify_download_token(token: str) -> dict:
    """Verify token and return payload"""
    return serializer.loads(token, salt="download-token", max_age=TOKEN_MAX_AGE)


def check_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    site: Optional[str] = Query(None)  # <-- site from query now
):
    if x_api_key not in API_KEY_MAP:
        raise HTTPException(status_code=401, detail="Invalid API key")

    allowed_sites = API_KEY_MAP[x_api_key]

    # Master key: access to all sites
    if "*" in allowed_sites:
        return True

    if site is None:
        raise HTTPException(status_code=400, detail="Missing 'site' query parameter")

    if site not in allowed_sites:
        raise HTTPException(
            status_code=403,
            detail=f"API key not allowed for site '{site}'"
        )

    return True

DATA_ROOT = Path('/data/level0b/polly24h')

@app.get("/api")
def api(
    site: str = Query(..., description="Site name"),
    date: Optional[str] = Query(None, description="Date in YYYYMMDD"),
    authorized: bool = Security(check_api_key)
):
  
    if site == None:
        site = 'all'
    if date == None:
        date = 'all'

    result=helper.device_at_site_timestamp(md_file=md_file, location=site, timestamp=date, device_type='polly')
    dict_object = helper.convert_db_2_dict(db=result)
    dev_dict = {}
    for device in dict_object.keys():
        dev_dict[device] = {}
        camp = dict_object[device]['history'][0]['pylarda_camp']
        con_files_ls = dict_object[device]['history'][0]['pylarda_connectorfile']
        if len(con_files_ls) > 0:
            con_file = con_files_ls[0]
            connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/{con_file}'
            connector_file_path = Path(connector_file)
            if connector_file_path.exists():
                print(connector_file)
                files = tromeda.get_files_from_connectorfile(tromeda_config_dict,connector_file,system_key='level0b' , start_date=date, end_date=date)
            else:
                files = None
        else:
            files = None
        if not files:
            continue
        if date in files.keys():
            pass
        else:
            continue
        result = [Path(f) for f in files[date]]
        result = [Path(*f.parts[-3:]) for f in result]
        dev_dict[device]['level0b_files'] = result
    #print(dev_dict)

    return dev_dict

@app.get("/apitoken")
def api_download(
    site: str = Query(..., description="Site name"),
    date: Optional[str] = Query(None, description="Date in YYYYMMDD"),
    authorized: bool = Security(check_api_key)
):
  
    if site == None:
        site = 'all'
    if date == None:
        date = 'all'

    result=helper.device_at_site_timestamp(md_file=md_file, location=site, timestamp=date, device_type='polly')
    dict_object = helper.convert_db_2_dict(db=result)
    dev_dict = {}
    token_ls = []
    for device in dict_object.keys():
        dev_dict[device] = {}
        camp = dict_object[device]['history'][0]['pylarda_camp']
        con_files_ls = dict_object[device]['history'][0]['pylarda_connectorfile']
        if len(con_files_ls) > 0:
            con_file = con_files_ls[0]
            connector_file = f'{pylarda_basedir}/larda-connectordump/{camp}/{con_file}'
            connector_file_path = Path(connector_file)
            if connector_file_path.exists():
                print(connector_file)
                files = tromeda.get_files_from_connectorfile(tromeda_config_dict,connector_file,system_key='level0b' , start_date=date, end_date=date)
            else:
                files = None
        else:
            files = None
        if not files:
            continue
        if date in files.keys():
            pass
        else:
            continue
        result = [Path(f) for f in files[date]]
        for element in result:
            # Create signed download token
            token = create_download_token(element, site)
            token_ls.append(token)
        #result = [Path(*f.parts[-3:]) for f in result]
        #dev_dict[device]['level0b_files'] = result
    #print(dev_dict)

    # return dev_dict
    return {"download_tokens": token_ls}#,
#            "download_urls": [f"/download?token={t}" for t in token_ls]}
#@app.get("/download/{filename:path}")
#def download_file(filename: str, authorized: bool = Security(check_api_key)):
    # Decode URL-encoded parts
#    filename = unquote(filename)
#@app.get("/download")
#def download(token: str = Query(...)):
@app.get("/download/{token:path}")
def download_file(token: str):
    try:
        data = verify_download_token(token)
        full_path = Path(data['filename'])
        print(full_path)
    except SignatureExpired:
        raise HTTPException(status_code=403, detail="Download token expired")
    except BadSignature:
        raise HTTPException(status_code=403, detail="Invalid download token")
    ## Build full path
    #full_path = (DATA_ROOT / filename).resolve()

   ## Security check: prevent path traversal
   # if DATA_ROOT not in full_path.parents:
   #     raise HTTPException(403, "Forbidden path")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(404, "File not found")

    # Stream the file in chunks
    def file_stream():
        with full_path.open("rb") as f:
            while chunk := f.read(1024*1024):  # 1 MB chunks
                yield chunk

    # Send file with just the basename as attachment
    return StreamingResponse(
        file_stream(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{full_path.name}"'}
    )

@app.get("/")
def index():
    return {"message": "POLLY API is running."}

