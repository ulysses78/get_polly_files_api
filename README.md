## Description
This tool allows fetching polly level0b data from the rsd2-server.

## Requirements:
For fetching data you only need the requests python-package in your python environment.
Furthermore an API-key is necessary to access the data.

## Usage
```
  -h, --help            show this help message and exit
  --site SITE           Site name
  --date DATE           Date in YYYYMMDD
  --api-key API_KEY     Use specific API key
  --download            Switch for downloading or just showing the results
  --download_dir DOWNLOAD_DIR
                        The folder to download to. Only necessary if download switch is activated
```

### Example usage:
Checking availability of polly level0b data:
```
fetch_polly_data.py --site leipzig --date 20260326 --api-key 1234-abcd-5678
```
returns:
```
{
    "arielle": {
        "level0b_files": [
            "arielle/2026/2026_03_26_Thu_ARI_00_00_01.nc"
        ]
    }
}
```

The ```--download``` switch will activate the download of available files:
```
fetch_polly_data.py --site leipzig --date 20260326 --api-key 1234-abcd-5678 --download
```

Optionally you can set the directory to download to with ```--download_dir```.
