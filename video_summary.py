import os
import logging
from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pydub import AudioSegment
import subprocess
import tempfile

def extract_audio_from_video(video_path, output_path):
    """Extract audio from video file."""
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(output_path, codec='pcm_s16le')
        video.close()
        return True
    except Exception as e:
        logging.error(f"❌ Error extracting audio: {str(e)}")
        return False

def transcribe_audio(audio_path):
    """Transcribe audio file using speech recognition."""
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        
        # Convert to WAV if needed
        if not audio_path.endswith('.wav'):
            wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
            AudioSegment.from_file(audio_path).export(wav_path, format='wav')
            audio_path = wav_path
        
        # Transcribe audio
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)
            
        text = recognizer.recognize_google(audio)
        return text
        
    except Exception as e:
        logging.error(f"❌ Error transcribing audio: {str(e)}")
        return None

def summarize_video(video_path, title, duration):
    """Generate a summary of the video content."""
    try:
        # Create temporary directory for audio
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract audio
            audio_path = os.path.join(temp_dir, 'audio.wav')
            if not extract_audio_from_video(video_path, audio_path):
                return None
            
            # Transcribe audio
            transcript = transcribe_audio(audio_path)
            if not transcript:
                return None
            
            # Generate summary using Gemini
            from video_insights import generate_gemini_content, SUMMARY_PROMPT
            
            # Add video metadata to transcript
            full_context = f"Title: {title}\nDuration: {duration} seconds\n\nTranscript:\n{transcript}"
            
            # Generate summary
            summary = generate_gemini_content(full_context, SUMMARY_PROMPT)
            return summary
            
    except Exception as e:
        logging.error(f"❌ Error summarizing video: {str(e)}")
        return None
