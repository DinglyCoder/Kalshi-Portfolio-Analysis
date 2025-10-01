import requests
import json
import time
from dotenv import load_dotenv
import os

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

load_dotenv()

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

# get all events from Kalshi API
def get_all_events():

    endpoint_path = "/trade-api/v2/events"

    url = f"https://api.elections.kalshi.com{endpoint_path}"
    response = requests.get(url)

    # Get the current timestamp
    current_timestamp = int(time.time() * 1000)

    public_key = os.getenv("KALSHI_PUBLIC_KEY")
    private_key = os.getenv("KALSHI_PRIVATE_KEY")

    print("Public Key:", public_key)
    print("Private Key:", private_key)

    signature = sign_request(private_key, current_timestamp, "GET", endpoint_path)

    headers = {
        "KALSHI-ACCESS-KEY": public_key,
        "KALSHI-ACCESS-TIMESTAMP": str(current_timestamp),
        "KALSHI-ACCESS-SIGNATURE": signature
    }

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
    

if __name__ == "__main__":
    events = get_all_events()
    if events:
        print(json.dumps(events, indent=4))
    else:
        print("No events found.")