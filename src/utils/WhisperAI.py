import subprocess

def WhisperAI(file):
  device = "cuda"
  diarization_process = subprocess.Popen(
    ["python3", "diarize_parallelNemo.py", "-a", file, "--device", device]
  ) 
  diarization_process.communicate()