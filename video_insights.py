import os
import time
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from constants import (
    MEDIA_FOLDER,
    SUMMARY_PROMPT,
    VIDEO_ANALYSIS_PROMPT,
    ERROR_MESSAGES
)

def initialize():
    """Initialize the video insights module."""
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("❌ API_KEY not found in .env file")
    genai.configure(api_key=api_key)

def get_insights(video_path):
    """Get insights from a video using Gemini Vision."""
    try:
        logging.info(f"🎥 Processing video: {video_path}")
        
        # Initialize Gemini model with the newer 1.5 Flash version
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Read video frames
        import cv2
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_interval = 30  # Capture one frame every second (assuming 30fps)
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % frame_interval == 0:
                # Convert frame to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to format expected by Gemini
                _, buffer = cv2.imencode('.jpg', frame_rgb)
                frames.append({
                    "mime_type": "image/jpeg",
                    "data": buffer.tobytes()
                })
                
                # Limit to max 10 frames to avoid token limits
                if len(frames) >= 10:
                    break
                    
            frame_count += 1
            
        cap.release()
        
        if not frames:
            raise ValueError("No frames could be extracted from the video")
            
        # Generate content with frames
        response = model.generate_content(
            contents=[VIDEO_ANALYSIS_PROMPT] + frames,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 2048
            }
        )
        
        return response.text
        
    except Exception as e:
        logging.error(f"❌ Error in get_insights: {str(e)}")
        raise

def save_video_file(file_data, filename):
    file_path = os.path.join(MEDIA_FOLDER, filename)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    return file_path

def generate_captions_from_audio(video_id):
    """Generate captions from video audio using speech recognition when no captions are available."""
    try:
        # Download video audio
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            logging.warning("❌ No audio stream available for this video")
            return None
            
        # Download to a temporary file
        temp_dir = os.path.join(MEDIA_FOLDER, "temp_audio")
        os.makedirs(temp_dir, exist_ok=True)
        audio_file = audio_stream.download(output_path=temp_dir)
        
        try:
            import speech_recognition as sr
            from pydub import AudioSegment
            
            # Convert to WAV format for speech recognition
            audio = AudioSegment.from_file(audio_file)
            wav_path = os.path.join(temp_dir, "temp_audio.wav")
            audio.export(wav_path, format="wav")
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
                
            # Perform speech recognition
            text = recognizer.recognize_google(audio_data)
            
            return text
            
        except Exception as e:
            logging.error(f"❌ Speech recognition failed: {str(e)}")
            return None
            
        finally:
            # Cleanup temporary files
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(os.path.join(temp_dir, "temp_audio.wav")):
                os.remove(os.path.join(temp_dir, "temp_audio.wav"))
            
    except Exception as e:
        logging.error(f"❌ Error generating captions from audio: {str(e)}")
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
            logging.error("❌ Invalid YouTube URL format")
            return None

        try:
            # Try to get manual captions first
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript = " ".join([item["text"] for item in transcript_list])
            return transcript
        except Exception as e:
            logging.warning(f"❌ No manual captions available: {str(e)}")
            try:
                # If manual captions fail, try auto-generated ones
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US'])
                transcript = " ".join([item["text"] for item in transcript_list])
                return transcript
            except Exception as e:
                logging.warning(f"❌ No auto-generated captions available: {str(e)}")
                try:
                    # If both fail, try to get any available transcript
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript(['en'])
                    transcript_list = transcript.fetch()
                    transcript = " ".join([item["text"] for item in transcript_list])
                    return transcript
                except Exception as e:
                    logging.warning(f"❌ No transcripts available at all: {str(e)}")
                    
                    # Try generating captions from audio as a last resort
                    logging.info("🎤 Attempting to generate captions from video audio...")
                    generated_transcript = generate_captions_from_audio(video_id)
                    if generated_transcript:
                        return generated_transcript
                    
                    logging.error("❌ Could not extract or generate video transcript")
                    return None
                    
    except Exception as e:
        logging.error(f"❌ Error in transcript extraction: {str(e)}")
        return None

def generate_gemini_content(transcript_text, prompt):
    """Generate content using Gemini Pro model."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        logging.error(f"❌ Error generating content: {str(e)}")
        raise

def process_youtube_video(youtube_url):
    """Process a YouTube video and return its summary."""
    try:
        transcript = extract_transcript_details(youtube_url)
        if transcript:
            summary = generate_gemini_content(transcript, SUMMARY_PROMPT)
            return "📝 Video Summary:\n\n" + summary
        return "❌ Could not generate summary. Please try another video."
    except Exception as e:
        logging.error(f"❌ Error processing YouTube video: {str(e)}")
        raise

def cleanup_video_file(file_path):
    """Clean up temporary video file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"🗑️ Cleaned up file: {file_path}")
    except Exception as e:
        logging.error(f"❌ Error cleaning up file {file_path}: {str(e)}")
