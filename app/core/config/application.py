"""Load config."""

import os
import json

# create log folder
FOLDER_PATH = "logs/archived"
if not os.path.exists(FOLDER_PATH):
    os.makedirs(FOLDER_PATH)


APPLICATION_CONFIG_PATH = os.path.join("resource", "application.json")
APPLICATION_CONFIG = {}
with open(file=APPLICATION_CONFIG_PATH, mode="r", encoding="utf-8") as f:
    APPLICATION_CONFIG = json.load(f)  # load config
