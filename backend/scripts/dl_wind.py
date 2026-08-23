import urllib.request

url = "https://archive.org/download/WindSoundEffect/Wind%20Sound%20Effect.mp3"
headers = {'User-Agent': 'Mozilla/5.0'}

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req) as response, open("wind.mp3", 'wb') as out_file:
    data = response.read()
    out_file.write(data)

print(f"Downloaded {len(data)} bytes")
