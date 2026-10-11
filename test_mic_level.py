import os
import subprocess
import numpy as np
import soundfile as sf

adb = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe")

print("Recording 2 seconds from speaker mic...")
subprocess.run(f'"{adb}" -s audio_84c8 shell "rm -f /tmp/test_mic.wav; /usr/bin/mic_test -f /tmp/test_mic.wav -d 2"', shell=True, check=True)

test_wav = "test_mic_output.wav"
subprocess.run(f'"{adb}" -s audio_84c8 pull /tmp/test_mic.wav {test_wav}', shell=True, check=True)

if os.path.exists(test_wav):
    data, sr = sf.read(test_wav)
    print(f"Sample rate: {sr}, Shape: {data.shape}, Dtype: {data.dtype}")
    if len(data.shape) > 1:
        channels = data.shape[1]
        for ch in range(channels):
            mono = data[:, ch]
            rms = float(np.sqrt(np.mean(mono**2)))
            peak = float(np.abs(mono).max())
            print(f"Channel {ch}: RMS={rms:.5f}, Peak={peak:.5f}")
    else:
        rms = float(np.sqrt(np.mean(data**2)))
        peak = float(np.abs(data).max())
        print(f"Mono: RMS={rms:.5f}, Peak={peak:.5f}")
else:
    print("Failed to pull mic file!")
