from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["localhost:3000", "http://localhost:3000", "localhost:3000/", "http://localhost:3000/"])

from scrim_finder.api import routes