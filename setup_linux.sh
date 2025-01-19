#!/bin/bash

echo "🚀 Setting up OmenFusionAi_Bot dependencies for Linux..."

# Update package list
sudo apt-get update

# Add FFmpeg repository (in case the default version has issues)
echo "📦 Adding FFmpeg repository..."
sudo add-apt-repository -y ppa:savoury1/ffmpeg4
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    ffmpeg \
    libmagic1 \
    libpq-dev \
    build-essential \
    portaudio19-dev \
    python3-pyaudio \
    libespeak1 \
    libavcodec-extra \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libpulse-dev \
    libasound2-dev \
    sox \
    libsox-fmt-all \
    libsox-fmt-mp3 \
    libsndfile1 \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev

# Install additional audio format support for Sox
echo "🎵 Installing additional audio format support..."
sudo apt-get install -y \
    libsox-fmt-all \
    libsox-fmt-mp3 \
    libmad0 \
    libid3tag0 \
    libvorbis-dev \
    libflac-dev \
    libogg-dev

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🌟 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Test audio setup
echo "🎵 Testing audio setup..."
python3 -c "
import speech_recognition as sr
from pydub import AudioSegment
import subprocess
import platform
import shutil

print('System Information:')
print(f'Platform: {platform.platform()}')
print(f'Python version: {platform.python_version()}')

print('\\nChecking Dependencies:')

# Check ffmpeg
try:
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        print(f'✅ ffmpeg installed at {ffmpeg_path}')
        print(f'Version: {result.stdout.split(\"\\n\")[0]}')
    else:
        print('❌ ffmpeg not found')
except Exception as e:
    print(f'❌ ffmpeg test failed: {str(e)}')

# Check sox
try:
    sox_path = shutil.which('sox')
    if sox_path:
        result = subprocess.run(['sox', '--version'], capture_output=True, text=True)
        print(f'✅ sox installed at {sox_path}')
        print(f'Version: {result.stdout.strip()}')
    else:
        print('❌ sox not found')
except Exception as e:
    print(f'❌ sox test failed: {str(e)}')

# Test speech recognition
try:
    recognizer = sr.Recognizer()
    print('✅ Speech recognizer initialized')
    print(f'Energy threshold: {recognizer.energy_threshold}')
    print(f'Dynamic energy threshold: {recognizer.dynamic_energy_threshold}')
except Exception as e:
    print(f'❌ Speech recognition test failed: {str(e)}')

# Test pydub
try:
    print('\\nTesting audio format support:')
    for fmt in ['mp3', 'wav', 'ogg', 'flac']:
        try:
            AudioSegment.from_file('/dev/null', format=fmt)
            print(f'✅ {fmt.upper()} support available')
        except Exception as e:
            print(f'❌ {fmt.upper()} support missing: {str(e)}')
except Exception as e:
    print(f'❌ Audio format test failed: {str(e)}')
"

echo "✅ Setup complete! You can now run the bot with: python app.py"
