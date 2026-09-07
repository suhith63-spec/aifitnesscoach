import subprocess
import sys

# Install required packages for low-latency voice
packages = [
    "elevenlabs==1.6.2",
    "pygame==2.5.2"
]

for package in packages:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed {package}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")

print("🎤 Low-latency voice integration ready!")