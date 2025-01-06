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
        video_file = genai.upload_file(path=video_path)

        while video_file.state.name == "PROCESSING":
            time.sleep(10)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError(ERROR_MESSAGES["processing_error"])

        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(
            [VIDEO_ANALYSIS_PROMPT, video_file],
            request_options={"timeout": 600}
        )
        
        insights = response.text
        genai.delete_file(video_file.name)
        return insights
        
    except Exception as e:
        logging.error(f"❌ Error in get_insights: {str(e)}")
        raise

def save_video_file(file_data, filename):
    file_path = os.path.join(MEDIA_FOLDER, filename)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    return file_path

def extract_transcript_details(youtube_video_url):
    """Extract transcript from YouTube video and handle cases where transcripts are unavailable."""
    try:
        # Extract video ID
        if "youtube.com/watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        else:
            raise ValueError("❌ Invalid YouTube URL format")

        try:
            # Try to get manual captions first
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception:
            try:
                # If manual captions fail, try auto-generated ones
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-US'])
            except Exception:
                # If both fail, try to get any available transcript
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                transcript = transcript_list.find_transcript(['en'])
                transcript_list = transcript.fetch()

        transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        logging.error(f"❌ Error extracting transcript: {str(e)}")
        raise ValueError("❌ Could not extract video transcript. The video might not have captions available.")

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
