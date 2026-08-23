import wave
import math
import random
import struct

def generate_wind(filename):
    sample_rate = 44100
    duration = 10.0
    num_samples = int(sample_rate * duration)

    print("Generating white noise...")
    noise = [random.uniform(-1.0, 1.0) for _ in range(num_samples)]
    
    print("Applying low-pass filters for mountain wind...")
    filtered = [0.0] * num_samples
    alpha_base = 0.02
    
    # Simulate gusts using low frequency oscillation
    for i in range(1, num_samples):
        # Gust frequency around 0.15 Hz
        gust = math.sin(2 * math.pi * 0.15 * i / sample_rate) 
        alpha = alpha_base + gust * 0.015
        if alpha < 0.005: 
            alpha = 0.005
        filtered[i] = filtered[i-1] + alpha * (noise[i] - filtered[i-1])

    # Normalize
    max_val = max(abs(x) for x in filtered)
    
    path = rf"c:\Users\devan\Downloads\ezgif-8ddbe56fb58fd3db-png-split\{filename}"
    wav_file = wave.open(path, 'w')
    wav_file.setnchannels(1) # Mono
    wav_file.setsampwidth(2) # 16-bit
    wav_file.setframerate(sample_rate)

    print("Writing to file...")
    for s in filtered:
        # Scale to 16-bit range and write
        val = int((s / max_val) * 32767 * 0.7) # 0.7 for slight headroom
        data = struct.pack('<h', val)
        wav_file.writeframesraw(data)
        
    wav_file.writeframes(b'')
    wav_file.close()
    print(f"Wind generated at {path}!")

if __name__ == '__main__':
    generate_wind('wind.wav')
