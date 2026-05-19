import requests
import json
import os
import base64

def check_env():
    print(f"Checking for any API key in env...")
    for k, v in os.environ.items():
        if 'API' in k.upper() or 'KEY' in k.upper() or 'TOKEN' in k.upper() or 'OPENAI' in k.upper() or 'ANTHROPIC' in k.upper():
            print(f"{k} is present")

check_env()
