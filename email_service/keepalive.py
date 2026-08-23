import os
import time
import urllib.request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# The public URL of the deployed email service (e.g. https://your-app.onrender.com)
# Pinging localhost inside a hosted environment might work, but pinging the public URL keeps the instance active.
SERVICE_URL = os.getenv('SELF_URL', 'http://localhost:5001')

def ping_service():
    health_url = f"{SERVICE_URL.rstrip('/')}/health"
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sending keepalive ping to {health_url}...")
    try:
        req = urllib.request.Request(
            health_url,
            headers={'User-Agent': 'Infacto-KeepAlive/1.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Success: Service is active.")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Warning: Received status code {response.status}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error: Failed to ping service: {e}")

if __name__ == '__main__':
    print("Keep-alive daemon started.")
    print(f"Target URL: {SERVICE_URL}")
    print("Interval: 5 minutes (300 seconds)")
    
    # Run indefinitely
    while True:
        ping_service()
        time.sleep(300)
