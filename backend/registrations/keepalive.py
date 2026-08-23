import threading
import time
import urllib.request
import os

def ping_loop():
    # Wait 10 seconds for the Django server to finish starting up
    time.sleep(10)
    
    # Get the production backend URL from env, default to local port 8001
    url = os.environ.get('BACKEND_URL') or os.environ.get('RENDER_EXTERNAL_URL')
    if not url:
        url = "http://127.0.0.1:8001"
    
    health_url = f"{url.rstrip('/')}/api/health/"
    print(f"[KeepAlive] Starting background self-ping loop at {health_url}")
    
    while True:
        try:
            req = urllib.request.Request(
                health_url, 
                headers={'User-Agent': 'Infacto-KeepAlive/1.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                status = response.getcode()
                # Print ping status for confirmation
                print(f"[KeepAlive] Health check ping successful: {status}")
        except Exception as e:
            print(f"[KeepAlive] Health check ping failed: {e}")
        
        # Sleep for 5 minutes (300 seconds)
        time.sleep(300)

def start_keepalive():
    # Start the daemon thread so it runs continuously in the background
    thread = threading.Thread(target=ping_loop, daemon=True)
    thread.start()
