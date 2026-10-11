import wave
import os
import subprocess
import google.generativeai as genai

API_KEY = 'YOUR_GEMINI_API_KEY_HERE'
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('models/gemini-2.5-flash-preview-tts')
resp = model.generate_content(
    'مرحبا عيوني شلونك، اني هيلين المساعد الذكي مالتك',
    generation_config={
        'response_modalities': ['AUDIO'],
        'speech_config': {
            'voice_config': {
                'prebuilt_voice_config': {
                    'voice_name': 'Kore'
                }
            }
        }
    }
)

raw = resp.candidates[0].content.parts[0].inline_data.data
if len(raw) % 2 != 0:
    raw = raw[:-1]

test_wav = 'test_tts_helen.wav'
with wave.open(test_wav, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(24000)
    wf.writeframes(raw)

print(f"Generated {test_wav}, size: {os.path.getsize(test_wav)} bytes")

adb = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe")
subprocess.run(f'"{adb}" -s audio_84c8 push {test_wav} /tmp/test_tts_helen.wav', shell=True, check=True)

# Test mplayer
print("Playing on speaker hardware...")
res = subprocess.run(f'"{adb}" -s audio_84c8 shell "mplayer -volume 100 /tmp/test_tts_helen.wav"', shell=True, capture_output=True, text=True)
print("Exit code:", res.returncode)
print("Output:\n", res.stdout)
if res.stderr:
    print("Stderr:\n", res.stderr)
