import os
import tempfile
import whisper
from typing import Optional, Union
import sys
import yt_dlp  

# Global model cache
_WHISPER_MODELS = {}

class YouTubeParser:
    """Parser to extract transcripts from YouTube videos."""
    
    def __init__(self, whisper_model_size: str = "base"):
        # Load model from cache or initialize
        global _WHISPER_MODELS
        if whisper_model_size not in _WHISPER_MODELS:
            try:
                print(f"Loading whisper model: {whisper_model_size}")  # Debug statement
                _WHISPER_MODELS[whisper_model_size] = whisper.load_model(whisper_model_size )
            except Exception as e:
                error_msg = f"Failed to load Whisper model: {str(e)}"
                print(error_msg)  # Print error for debugging
                raise RuntimeError(error_msg)
                
        self.whisper_model = _WHISPER_MODELS[whisper_model_size]
    
    def download_audio(self, url: str, output_path: Optional[str] = None) -> str:
        """
        Download audio from a YouTube video using yt-dlp Python package.
        
        Args:
            url: YouTube URL
            output_path: Path to save the audio file. If None, a temporary file is used.
            
        Returns:
            Path to the downloaded audio file
        """
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
        
        # Remove file extension for yt-dlp output template
        output_template = output_path.rsplit('.', 1)[0]
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_template,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return output_path
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcription text
        """
        result = self.whisper_model.transcribe(audio_path)
        return result["text"]
    
    def parse(self, url: str, cleanup: bool = True) -> str:
        try:
            audio_path = self.download_audio(url)
            if not audio_path or not os.path.exists(audio_path):
                return "❌ Failed to download audio from YouTube."
            result = self.whisper_model.transcribe(audio_path)
            transcript = result.get("text", "").strip()
            if cleanup and audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
            return transcript if transcript else "❌ No transcript found."
        except Exception as e:
            return f"❌ Error during YouTube transcription: {str(e)}"


# filepath: c:\Users\abhis\ScopeAI\src\parser\youtube_parser.py
def extract_youtube_transcript(url, use_whisper=True):
    """Extract transcript from YouTube video."""
    if use_whisper:
        parser = YouTubeParser(whisper_model_size="tiny")
        return parser.parse(url)  # Changed from transcribe() to parse()
    else:
        # Get YouTube's own captions using youtube_transcript_api
        from youtube_transcript_api import YouTubeTranscriptApi
        video_id = url.split("v=")[1].split("&")[0]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item['text'] for item in transcript_list])


if __name__ == "__main__":
    # Example usage
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        transcript = extract_youtube_transcript(url)
        print(transcript)
    else:
        print("Please provide a YouTube URL as a command-line argument")