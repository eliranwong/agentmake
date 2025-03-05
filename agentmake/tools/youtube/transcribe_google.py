from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["youtube-transcript-api"]
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter

TOOL_SYSTEM = f"""You are an good at identifying a YouTube url from user request. Return an empty string '' for parameter `url` if no YouTube url is given."""

TOOL_SCHEMA = {
    "name": "transcribe_youtube_audio_google",
    "description": "Transcribe YouTube video into text with Google service",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Youtube url given by user",
            },
        },
        "required": ["url"],
    },
}

def transcribe_youtube_audio_google(url: str="", **kwargs):

    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter

    from agentmake import AGENTMAKE_USER_DIR, getCurrentDateTime
    from pathlib import Path
    import re, os

    def get_video_id(url):
        """
        Extract video ID from YouTube URL
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            str: YouTube video ID
        """
        # Handle different URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu.be\/)([^&\n?#]+)',
            r'(?:youtube\.com\/embed\/)([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def download_transcript(video_url, output_file=None):
        """
        Download transcript from a YouTube video
        
        Args:
            video_url (str): YouTube video URL
            output_file (str, optional): Path to save the transcript. If None, prints to console.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get video ID
            video_id = get_video_id(video_url)
            if not video_id:
                print("Error: Could not extract video ID from URL")
                return False
            
            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Format transcript
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript)
            
            # Save or print transcript
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_transcript)
                #print(f"Transcript saved to {output_file}")
            print("```transcription")
            print(formatted_transcript)
            print("```")
            return True
            
        except Exception as e:
            print(f"Error downloading transcript: {str(e)}")
            return False

    # save a copy
    transcriptions_dir = os.path.join(AGENTMAKE_USER_DIR, "transcriptions")
    Path(transcriptions_dir).mkdir(parents=True, exist_ok=True)
    transcriptions_file = os.path.join(transcriptions_dir, getCurrentDateTime())
    download_transcript(url, transcriptions_file)
    return ""

TOOL_FUNCTION = transcribe_youtube_audio_google
