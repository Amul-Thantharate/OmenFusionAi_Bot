import yt_dlp
import os
import time
from pathlib import Path

VIDEO_DIR = "downloaded_videos"
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

def ensure_video_dir():
    """Create video directory if it doesn't exist."""
    os.makedirs(VIDEO_DIR, exist_ok=True)

def get_video_info(url):
    """Get video information without downloading."""
    ydl_opts = {
        'format': 'best',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            return None

def download_and_compress_video(url):
    """Download video and ensure it's under 20MB."""
    ensure_video_dir()
    
    # First try with lower quality
    ydl_opts = {
        'format': 'worst[ext=mp4]',
        'outtmpl': os.path.join(VIDEO_DIR, '%(title)s.%(ext)s'),
        'quiet': True
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                if file_size <= MAX_FILE_SIZE:
                    return filename, None
                else:
                    os.remove(filename)
                    return None, "Video size exceeds 20MB limit even at lowest quality"
            
            return None, "Failed to download video"
    except Exception as e:
        return None, f"Error downloading video: {str(e)}"

def clear_videos():
    """Remove all downloaded videos."""
    if os.path.exists(VIDEO_DIR):
        for file in os.listdir(VIDEO_DIR):
            try:
                os.remove(os.path.join(VIDEO_DIR, file))
            except Exception as e:
                print(f"Error deleting {file}: {str(e)}")
        return "✅ All downloaded videos have been cleared."
    return "No videos to clear."

def get_downloaded_videos():
    """Get list of downloaded videos with their sizes."""
    if not os.path.exists(VIDEO_DIR):
        return []
    
    videos = []
    for file in os.listdir(VIDEO_DIR):
        path = os.path.join(VIDEO_DIR, file)
        size = os.path.getsize(path)
        size_mb = size / (1024 * 1024)  # Convert to MB
        videos.append({
            'name': file,
            'size': f"{size_mb:.2f}MB",
            'path': path
        })
    return videos
