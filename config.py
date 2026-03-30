import os

API_KEY = os.getenv("MYAPI_KEY")

if API_KEY is None:
        raise RuntimeError("Environment variable MYAPI_KEY is not set!")

