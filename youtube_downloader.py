import yt_dlp

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
ydl_opts = {
    'format': 'best[height<=720]',  # Limit to 720p to avoid format issues
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': False,
    'no_warnings': False,
    'extract_flat': False,
    'no_check_certificates': True,
    'ignoreerrors': True,
    'no_playlist': True,  # Avoid downloading playlists accidentally
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',  # Convert to MP4 if needed
    }]
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("Starting download...")
        ydl.download([url])
        print("Download completed successfully!")
except Exception as e:
    print(f"An error occurred: {str(e)}")
    # Try with an even simpler format if first attempt fails
    print("Trying alternate format...")
    ydl_opts['format'] = 'best'  # Fallback to best available format
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print("Download completed with alternate format!")
    except Exception as e:
        print(f"Second attempt failed: {str(e)}")
