import os
import json

folder_path = "logs/archived"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    
APPLICATION_CONFIG_PATH = os.path.join('resource', 'application.json')
APPLICATION_CONFIG = {}
with open(APPLICATION_CONFIG_PATH, 'r') as f:
    APPLICATION_CONFIG = json.load(f)