Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\Th3painter\Documents\antigravity\focused-bardeen"
WshShell.Run "python ai_smart_speaker.py", 0, False
