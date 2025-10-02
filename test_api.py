import requests
import json
import time
from dotenv import load_dotenv
import os

import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()

base_url = "https://api.elections.kalshi.com"
public_key = os.getenv("KALSHI_PUBLIC_KEY")
private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")


def load_private_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(),password=None)

def sign_request(private_key, timestamp, method, path):
    # Create the message to sign
    message = f"{timestamp}{method}{path}".encode('utf-8')

    # Sign with RSA-PSS
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )

    # Return base64 encoded
    return base64.b64encode(signature).decode('utf-8')

def get(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# get all events from Kalshi API
def get_all_events(params=None):
    all_events = []
    cursor = None
    endpoint_path = "/trade-api/v2/events"
    url = f"{base_url}{endpoint_path}"

    # Get the current timestamp
    current_timestamp = int(time.time() * 1000)

    private_key = load_private_key(private_key_path)
    signature = sign_request(private_key, current_timestamp, "GET", endpoint_path)

    headers = {
        "KALSHI-ACCESS-KEY": public_key,
        "KALSHI-ACCESS-TIMESTAMP": str(current_timestamp),
        "KALSHI-ACCESS-SIGNATURE": signature
    }

    while True:
        print(f"Fetching events with cursor: {cursor}")
        if cursor:
            params = {
                'limit': 200,
            }
            params['cursor'] = cursor

        response = get(url, headers, params)

        if response and 'events' in response:
            all_events.extend(response['events'])
            cursor = response.get('cursor')
            if not cursor:
                break
        else:
            break

    return all_events 
    

if __name__ == "__main__":
    events = get_all_events()
    print(f"Total events fetched: {len(events)}")

    

    