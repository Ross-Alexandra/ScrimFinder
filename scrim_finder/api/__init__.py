from flask import Flask
from flask_cors import CORS
import os

def _origins(verbose=False):
    dev_origins = [
        "http://localhost:3000",
        "http://localhost:3000/",
        "https://localhost:3000",
        "https://localhost:3000/",
        "http://localhost:34363",
        "http://localhost:34363/",
        "https://localhost:34363",
        "https://localhost:34363/",
        "http://172.28.1.1/",
        "http://172.28.1.1",
        "https://172.28.1.1/",
        "https://172.28.1.1",
        "http://172.28.1.3:34362/",
        "http://172.28.1.3:34362",
        "https://172.28.1.3:34362",
        "https://172.28.1.3:34362"
    ]

    prod_origins = [
        "http://scrimsearch.com",
        "http://scrimsearch.com/",
        "https://scrimsearch.com",
        "https://scrimsearch.com/",
        "http://www.scrimsearch.com",
        "http://www.scrimsearch.com/",
        "https://www.scrimsearch.com",
        "https://www.scrimsearch.com/",
        "http://scrimsearch.theserverproject.com/",
        "http://scrimsearch.theserverproject.com",
        "https://scrimsearch.theserverproject.com/",
        "https://scrimsearch.theserverproject.com/",
        "http://154.5.209.170/",
        "http://154.5.209.170",
        "https://154.5.209.170/",
        "https://154.5.209.170",
        "http://192.168.1.70:34363/",
        "http://192.168.1.70:34363",
        "https://192.168.1.70:34363/",
        "https://192.168.1.70:34363",
    ]

    if os.getenv("SCRIM_FINDER_ENVIRONMENT", None) == "DEVELOPMENT":
        origins = dev_origins + prod_origins
    else:
        origins = prod_origins

    if verbose:
        print(origins)
    
    return origins

app = Flask(__name__)
CORS(app, origins=_origins(verbose=False))

from scrim_finder.api import routes