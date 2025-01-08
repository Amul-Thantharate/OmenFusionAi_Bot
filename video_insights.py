import os
import time
import logging
import subprocess
from pathlib import Path
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
import google.generativeai as genai
from dotenv import load_dotenv
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import re
import browser_cookie3

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Constants
MEDIA_FOLDER = Path(__file__).parent / "medias"
MEDIA_FOLDER.mkdir(parents=True, exist_ok=True)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
genai.configure(api_key=GEMINI_API_KEY)

# Prompts
SUMMARY_PROMPT = """
Please provide a concise summary of this video content. Focus on:
1. Main topics and key points
2. Important insights or findings
3. Any conclusions or recommendations

Keep the summary clear and well-structured.
"""
VIDEO_ANALYSIS_PROMPT = """
Please analyze the video content and provide insights on:
1. Key events or scenes
2. Character interactions or relationships
3. Any notable themes or symbolism

Keep the analysis clear and well-structured.
"""

def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/shorts/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def initialize():
    """Initialize the video insights module."""
    if not MEDIA_FOLDER.exists():
        MEDIA_FOLDER.mkdir(parents=True, exist_ok=True)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    genai.configure(api_key=api_key)

def get_insights(video_path):
    """Get insights from a video using Gemini Vision."""
    try:
        # Initialize Gemini model with the newer 1.5 Flash version
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read video file
        with open(video_path, 'rb') as f:
            video_data = f.read()
            
        # Create video part
        video_part = {
            'mime_type': 'video/mp4',
            'data': video_data
        }
        
        # Generate content with specific config
        response = model.generate_content(
            contents=[
                "Analyze this video and describe what's happening, including key events, objects, and people. Be concise but detailed.",
                video_part
            ],
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048
            }
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error in get_insights: {str(e)}")
        raise

def save_video_file(file_data, filename):
    file_path = MEDIA_FOLDER / filename
    with open(file_path, 'wb') as f:
        f.write(file_data)
    return file_path

def is_linux():
    """Check if running on Linux."""
    import platform
    return platform.system().lower() == 'linux'

def check_audio_dependencies():
    """Check and log audio dependencies status."""
    import subprocess
    import shutil
    
    deps = {
        'ffmpeg': False,
        'sox': False,
        'python-magic': False,
        'libav': False
    }
    
    try:
        # Check ffmpeg
        if shutil.which('ffmpeg'):
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            deps['ffmpeg'] = result.returncode == 0
            logging.info(f"FFmpeg version: {result.stdout.split('\\n')[0] if result.returncode == 0 else 'Not found'}")
    except Exception as e:
        logging.error(f"FFmpeg check failed: {str(e)}")
    
    try:
        # Check sox
        if shutil.which('sox'):
            result = subprocess.run(['sox', '--version'], capture_output=True, text=True)
            deps['sox'] = result.returncode == 0
            logging.info(f"SoX version: {result.stdout.split('\\n')[0] if result.returncode == 0 else 'Not found'}")
    except Exception as e:
        logging.error(f"SoX check failed: {str(e)}")
    
    try:
        # Check python-magic
        import magic
        deps['python-magic'] = True
        logging.info("python-magic is installed")
    except ImportError:
        logging.error("python-magic is not installed")
    
    try:
        # Check libav
        if shutil.which('avconv') or shutil.which('ffmpeg'):
            deps['libav'] = True
            logging.info("libav/ffmpeg is available")
    except Exception as e:
        logging.error(f"libav check failed: {str(e)}")
    
    return deps

def get_video_info(video_id):
    """Get video info using innertube API to bypass restrictions."""
    import requests
    import json
    
    try:
        # Use innertube API
        data = {
            "context": {
                "client": {
                    "clientName": "ANDROID",
                    "clientVersion": "17.31.35",
                    "androidSdkVersion": 30,
                }
            },
            "videoId": video_id
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
        }
        
        response = requests.post(
            'https://www.youtube.com/youtubei/v1/player',
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()
        return None
        
    except Exception as e:
        logging.error(f"Error getting video info: {str(e)}")
        return None

def get_browser_cookies():
    """Get cookies from installed browsers."""
    cookies = {}
    browsers = [
        (browser_cookie3.chrome, "Chrome"),
        (browser_cookie3.firefox, "Firefox"),
        (browser_cookie3.edge, "Edge"),
        (browser_cookie3.opera, "Opera"),
        (browser_cookie3.brave, "Brave"),
    ]
    
    for browser_func, name in browsers:
        try:
            browser_cookies = browser_func(domain_name=".youtube.com")
            if browser_cookies:
                logger.info(f"Found cookies in {name}")
                cookies.update({cookie.name: cookie.value for cookie in browser_cookies})
                break
        except Exception as e:
            logger.debug(f"Could not get cookies from {name}: {str(e)}")
    
    return cookies

def download_youtube_audio(video_id, output_dir):
    """Download YouTube audio using yt-dlp with browser cookies."""
    import yt_dlp
    import tempfile
    
    try:
        # Get browser cookies
        cookies = get_browser_cookies()
        if not cookies:
            logging.warning("No browser cookies found. Download may fail.")
        
        # Create a temporary cookie file
        cookie_file = None
        if cookies:
            cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            with open(cookie_file.name, 'w') as f:
                for cookie in cookies:
                    f.write(f"{cookie}\tTRUE\t/\t{'TRUE' if cookie.startswith('SECURE') else 'FALSE'}\t{cookie.split(';')[1]}\t{cookie.split(';')[0]}\n")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, 'audio.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'verbose': False,
            'cookiefile': cookie_file.name if cookie_file else None,
            # Add custom headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
            }
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        logging.info(f"Downloading audio from: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # Find the output file
        wav_file = os.path.join(output_dir, 'audio.wav')
        if os.path.exists(wav_file) and os.path.getsize(wav_file) > 0:
            logging.info(f"Successfully downloaded audio: {os.path.getsize(wav_file)} bytes")
            return wav_file
            
        logging.error("Audio file not found after download")
        return None
        
    except Exception as e:
        logging.error(f"Error downloading audio: {str(e)}")
        return None
        
    finally:
        # Clean up cookie file
        if cookie_file:
            try:
                os.unlink(cookie_file.name)
            except:
                pass

def download_youtube_video(video_id, output_dir):
    """Download YouTube video using yt-dlp with browser cookies."""
    import yt_dlp
    import tempfile
    
    try:
        # Get browser cookies
        cookies = get_browser_cookies()
        if not cookies:
            logging.warning("No browser cookies found. Download may fail.")
        
        # Create a temporary cookie file
        cookie_file = None
        if cookies:
            cookie_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            with open(cookie_file.name, 'w') as f:
                for cookie in cookies:
                    f.write(f"{cookie}\tTRUE\t/\t{'TRUE' if cookie.startswith('SECURE') else 'FALSE'}\t{cookie.split(';')[1]}\t{cookie.split(';')[0]}\n")
        
        # Configure yt-dlp options for video download
        ydl_opts = {
            'format': 'best[height<=720]',  # 720p or lower to save space
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'verbose': False,
            'cookiefile': cookie_file.name if cookie_file else None,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'DNT': '1',
            }
        }
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        logging.info(f"Downloading video from: {url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)
            
        if os.path.exists(video_file) and os.path.getsize(video_file) > 0:
            logging.info(f"Successfully downloaded video: {os.path.getsize(video_file)} bytes")
            return video_file
            
        logging.error("Video file not found after download")
        return None
        
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        return None
        
    finally:
        # Clean up cookie file
        if cookie_file:
            try:
                os.unlink(cookie_file.name)
            except:
                pass

def generate_captions_from_audio(video_id):
    """Generate captions from video audio using speech recognition when no captions are available."""
    try:
        # Set up debug logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Check system and dependencies
        logging.info(f"Running on Linux: {is_linux()}")
        deps = check_audio_dependencies()
        logging.info(f"Audio dependencies status: {deps}")
        
        # Create temp directory
        temp_dir = os.path.join(MEDIA_FOLDER, f"temp_audio_{video_id}_{int(time.time())}")
        os.makedirs(temp_dir, exist_ok=True)
        logging.info(f"Created temp directory: {temp_dir}")
        
        try:
            # Download audio using yt-dlp
            wav_path = download_youtube_audio(video_id, temp_dir)
            if not wav_path:
                return None
            
            # Initialize recognizer with adjusted settings
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source)
                # Record audio with increased duration
                audio_data = recognizer.record(source)
                logging.info("Audio data recorded successfully")
                
            # Perform speech recognition with error handling and retries
            for attempt in range(3):
                try:
                    logging.info(f"Speech recognition attempt {attempt + 1}")
                    text = recognizer.recognize_google(audio_data)
                    if text:
                        logging.info("Speech recognition successful")
                        return text
                    logging.warning(f"Empty transcription result on attempt {attempt + 1}")
                except sr.UnknownValueError:
                    logging.warning(f"Speech recognition failed on attempt {attempt + 1}")
                except sr.RequestError as e:
                    logging.error(f"Speech recognition service error: {str(e)}")
                    break
                
                if attempt < 2:
                    time.sleep(2)
            
            logging.error("All speech recognition attempts failed")
            return None
            
        except Exception as e:
            logging.error(f"Speech recognition failed: {str(e)}")
            return None
            
        finally:
            # Cleanup temporary files
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
                    logging.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logging.error(f"Error cleaning up temporary directory: {str(e)}")
            
    except Exception as e:
        logging.error(f"Error generating captions from audio: {str(e)}")
        return None

def extract_transcript_details(youtube_video_url):
    """Extract transcript from YouTube video and handle cases where transcripts are unavailable."""
    try:
        # Extract video ID
        if "youtube.com/watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            logging.error("Invalid YouTube URL format")
            return None

        try:
            # Try to get manual captions first
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript = " ".join([item["text"] for item in transcript_list])
            return transcript
        except Exception as e:
            logging.warning(f"No manual captions available: {str(e)}")
            try:
                # If manual captions fail, try auto-generated ones
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US'])
                transcript = " ".join([item["text"] for item in transcript_list])
                return transcript
            except Exception as e:
                logging.warning(f"No auto-generated captions available: {str(e)}")
                try:
                    # If both fail, try to get any available transcript
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript(['en'])
                    transcript_list = transcript.fetch()
                    transcript = " ".join([item["text"] for item in transcript_list])
                    return transcript
                except Exception as e:
                    logging.warning(f"No transcripts available at all: {str(e)}")
                    
                    # Try generating captions from audio as a last resort
                    logging.info("Attempting to generate captions from video audio...")
                    generated_transcript = generate_captions_from_audio(video_id)
                    if generated_transcript:
                        return generated_transcript
                    
                    logging.error("Could not extract or generate video transcript")
                    return None
                    
    except Exception as e:
        logging.error(f"Error in transcript extraction: {str(e)}")
        return None

def generate_gemini_content(transcript_text, prompt):
    """Generate content using Gemini Pro model."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        logging.error(f"Error generating content: {str(e)}")
        raise

def process_youtube_video(video_id):
    """Process YouTube video: download, summarize, and cleanup."""
    try:
        # Create temp directory
        temp_dir = os.path.join(MEDIA_FOLDER, f"temp_video_{video_id}_{int(time.time())}")
        os.makedirs(temp_dir, exist_ok=True)
        logging.info(f"Created temp directory: {temp_dir}")
        
        try:
            # Download video
            video_file = download_youtube_video(video_id, temp_dir)
            if not video_file:
                return None
                
            # Get video info for the summary
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                video_info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                title = video_info.get('title', 'Unknown Title')
                duration = video_info.get('duration', 0)
                
            # Pass to summarize function
            from video_summary import summarize_video
            summary = summarize_video(video_file, title, duration)
            
            return summary
            
        except Exception as e:
            logging.error(f"Error processing video: {str(e)}")
            return None
            
        finally:
            # Cleanup temporary directory and files
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
                    logging.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logging.error(f"Error cleaning up temporary directory: {str(e)}")
            
    except Exception as e:
        logging.error(f"Error in process_youtube_video: {str(e)}")
        return None

async def handle_youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the youtube_summary command."""
    try:
        # Check if URL is provided
        if not context.args:
            await update.message.reply_text(
                "Please provide a YouTube URL. Example: youtube_summary https://youtu.be/VIDEO_ID"
            )
            return

        url = context.args[0]
        video_id = extract_video_id(url)
        
        if not video_id:
            await update.message.reply_text(
                "Invalid YouTube URL. Please provide a valid YouTube video URL."
            )
            return

        # Send processing message
        processing_msg = await update.message.reply_text(
            "Processing your YouTube video... This may take a few minutes."
        )

        try:
            # Configure yt-dlp with advanced options
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(MEDIA_FOLDER / f'{video_id}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                # Advanced options to bypass restrictions
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],  # Use android client
                        'player_skip': ['webpage', 'configs'],  # Skip unnecessary data
                    }
                },
                # Use various clients to avoid bot detection
                'external_downloader_args': ['--add-header', 'User-Agent:Mozilla/5.0 (Android 12; Mobile; rv:68.0) Gecko/68.0 Firefox/96.0'],
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Android 12; Mobile; rv:68.0) Gecko/68.0 Firefox/96.0',
                    'Accept-Language': 'en-US,en;q=0.5',
                },
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info = ydl.extract_info(url, download=True)
                except Exception as first_error:
                    logger.warning(f"First attempt failed: {str(first_error)}")
                    # Try alternate format on failure
                    ydl_opts.update({
                        'format': 'worstaudio/worst',  # Try worst quality as fallback
                        'extractor_args': {
                            'youtube': {
                                'player_client': ['ios'],  # Try iOS client
                            }
                        }
                    })
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                        info = ydl2.extract_info(url, download=True)
                
                title = info.get('title', 'Video')
                duration = info.get('duration', 0)
                
                await processing_msg.edit_text(
                    f"Downloaded: {title}\n"
                    f"Duration: {duration//60}:{duration%60:02d}\n"
                    "Generating summary..."
                )

            # Initialize Gemini
            model = genai.GenerativeModel('gemini-pro')
            
            # Generate summary
            response = model.generate_content(
                f"Title: {title}\nDuration: {duration//60}:{duration%60:02d}\n\n{SUMMARY_PROMPT}"
            )
            
            summary = response.text.strip()
            
            # Send summary
            await processing_msg.edit_text(
                f"Summary of '{title}'\n\n{summary}\n\n"
                f"Video: {url}"
            )

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            await processing_msg.edit_text(
                f"Error processing video: {str(e)}\n"
                "Please try again or contact support if the issue persists."
            )

        finally:
            # Cleanup
            try:
                for file in MEDIA_FOLDER.glob(f"{video_id}.*"):
                    file.unlink()
            except Exception as e:
                logger.error(f"Error cleaning up files: {str(e)}")

    except Exception as e:
        logger.error(f"Error in handle_youtube_command: {str(e)}")
        await update.message.reply_text(
            "An unexpected error occurred. Please try again later."
        )

def cleanup_video_file(file_path):
    """Clean up temporary video file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logging.error(f"Error cleaning up file {file_path}: {str(e)}")
