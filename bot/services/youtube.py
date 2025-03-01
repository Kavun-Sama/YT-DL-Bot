"""
YouTube service for downloading videos and audio using yt-dlp
"""
import os
import re
import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from pathlib import Path
import uuid

import yt_dlp
import aiofiles

from bot.config import config


class YouTubeService:
    """Service for working with YouTube"""
    
    # Regular expression for YouTube URL validation
    YOUTUBE_URL_PATTERN = r'(?:https?:\/\/)?(?:www\.)?(?:(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/))([a-zA-Z0-9_-]{11})(?:\S+)?'
    
    # Standard video resolutions
    RESOLUTIONS = {
        "144p": 144,
        "240p": 240,
        "360p": 360,
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
        "1440p": 1440,
        "2160p": 2160,
    }
    
    def __init__(self, download_dir: str = None):
        """
        Initialize the service
        
        Args:
            download_dir: Directory for downloaded files
        """
        self.download_dir = download_dir or config.download_dir
        self.logger = logging.getLogger(__name__)
    
    def is_valid_youtube_url(self, url: str) -> bool:
        """
        Check if the URL is a valid YouTube link
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if the URL is a YouTube link, otherwise False
        """
        if not url:
            return False
            
        # Clean URL from extra characters
        cleaned_url = url.strip()
        # Remove @ and other unwanted characters from the beginning of URL
        cleaned_url = re.sub(r'^[@\s]+', '', cleaned_url)
        
        # Simple check for youtube.com or youtu.be in URL
        if 'youtube.com' in cleaned_url or 'youtu.be' in cleaned_url:
            self.logger.debug("URL contains youtube.com or youtu.be - considered valid")
            return True
        
        # Use regular expression as a fallback
        result = bool(re.search(self.YOUTUBE_URL_PATTERN, cleaned_url))
        self.logger.debug(f"Regular expression validation result: {result}")
        
        return result
    
    async def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get video information
        
        Args:
            url: Video URL
            
        Returns:
            Dict[str, Any]: Video information
        """
        # Clean URL from extra characters
        cleaned_url = url.strip()
        cleaned_url = re.sub(r'^[@\s]+', '', cleaned_url)
        
        self.logger.info(f"Getting video information: {cleaned_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        try:
            # Run in a separate thread to avoid blocking the main thread
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._extract_info, cleaned_url, ydl_opts)
            self.logger.info(f"Successfully got video information: {info.get('title', 'Unknown')}")
            return info
        except Exception as e:
            self.logger.error(f"Error getting video information: {e}")
            raise
    
    async def get_available_formats(self, url: str) -> List[str]:
        """
        Get available video formats
        
        Args:
            url: Video URL
            
        Returns:
            List[str]: List of available video formats (resolutions)
        """
        # Clean URL from extra characters
        cleaned_url = url.strip()
        cleaned_url = re.sub(r'^[@\s]+', '', cleaned_url)
        
        self.logger.info(f"Getting available formats for video: {cleaned_url}")
        
        try:
            # Get video information
            info = await self.get_video_info(cleaned_url)
            formats = info.get('formats', [])
            
            # Collect available resolutions
            available_heights = set()
            for fmt in formats:
                if fmt.get('vcodec') != 'none':  # Only video formats
                    height = fmt.get('height')
                    if height:
                        available_heights.add(height)
            
            self.logger.debug(f"Available video heights: {sorted(available_heights)}")
            
            # Match with our standard resolutions
            available_formats = []
            for format_name, height in sorted(self.RESOLUTIONS.items(), key=lambda x: x[1]):
                # Check if there are formats with height close to our standard resolution
                for available_height in sorted(available_heights):
                    # If available height is close to standard (within 10% or 50 pixels)
                    height_diff = abs(available_height - height)
                    if height_diff <= max(height * 0.1, 50):
                        available_formats.append(format_name)
                        break
            
            # If no format found, add all standard formats
            # for which there is video with lower or equal resolution
            if not available_formats:
                max_height = max(available_heights) if available_heights else 720
                for format_name, height in self.RESOLUTIONS.items():
                    if height <= max_height:
                        available_formats.append(format_name)
            
            # Sort formats by quality
            available_formats.sort(key=lambda x: self.RESOLUTIONS[x])
            
            self.logger.info(f"Available formats: {available_formats}")
            return available_formats
        except Exception as e:
            self.logger.error(f"Error getting available formats: {e}")
            # In case of error, return standard set of formats
            return ["144p", "240p", "360p", "480p", "720p", "1080p"]
    
    def _extract_info(self, url: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract video information (synchronous function for running in a separate thread)
        
        Args:
            url: Video URL
            options: Options for yt-dlp
            
        Returns:
            Dict[str, Any]: Video information
        """
        with yt_dlp.YoutubeDL(options) as ydl:
            return ydl.extract_info(url, download=False)
    
    async def download_audio(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Download audio from video
        
        Args:
            url: Video URL
            
        Returns:
            Tuple[Optional[str], Optional[str]]: File path and filename, or None in case of error
        """
        # Clean URL from extra characters
        cleaned_url = url.strip()
        cleaned_url = re.sub(r'^[@\s]+', '', cleaned_url)
        
        self.logger.info(f"Downloading audio from video: {cleaned_url}")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        output_path = os.path.join(self.download_dir, f"{file_id}.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            # Get video information for filename
            info = await self.get_video_info(cleaned_url)
            title = info.get('title', 'audio')
            
            # Run download in a separate thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download, cleaned_url, ydl_opts)
            
            # Find downloaded file
            downloaded_file = None
            for file in os.listdir(self.download_dir):
                if file.startswith(file_id) and file.endswith('.mp3'):
                    downloaded_file = os.path.join(self.download_dir, file)
                    break
            
            if downloaded_file:
                # Rename file to contain video title
                safe_title = re.sub(r'[^\w\-_\. ]', '_', title)
                new_filename = f"{safe_title}.mp3"
                new_path = os.path.join(self.download_dir, new_filename)
                
                # If file with such name already exists, add unique identifier
                if os.path.exists(new_path):
                    new_filename = f"{safe_title}_{file_id[:8]}.mp3"
                    new_path = os.path.join(self.download_dir, new_filename)
                
                os.rename(downloaded_file, new_path)
                return new_path, new_filename
            
            return None, None
        except Exception as e:
            self.logger.error(f"Error downloading audio: {e}")
            return None, None
    
    async def download_video(self, url: str, quality: str = "720p") -> Tuple[Optional[str], Optional[str]]:
        """
        Download video
        
        Args:
            url: Video URL
            quality: Video quality
            
        Returns:
            Tuple[Optional[str], Optional[str]]: File path and filename, or None in case of error
        """
        # Clean URL from extra characters
        cleaned_url = url.strip()
        cleaned_url = re.sub(r'^[@\s]+', '', cleaned_url)
        
        self.logger.info(f"Downloading video: {cleaned_url}, quality: {quality}")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        output_path = os.path.join(self.download_dir, f"{file_id}.%(ext)s")
        
        # Get height for selected quality
        height = self.RESOLUTIONS.get(quality, 720)
        
        # Form format string for yt-dlp
        # Always download video and audio separately, then merge
        format_code = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
        
        self.logger.info(f"Using format for quality {quality}: {format_code}")
        
        # Settings for video download
        ydl_opts = {
            'format': format_code,
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            # Add options for more reliable downloading
            'retries': 10,  # Number of retries
            'fragment_retries': 10,  # Number of fragment retries
            'skip_unavailable_fragments': True,  # Skip unavailable fragments
            'keepvideo': False,  # Don't keep original video files
        }
        
        try:
            # Get video information for filename
            info = await self.get_video_info(cleaned_url)
            title = info.get('title', 'video')
            
            # Run download in a separate thread
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._download, cleaned_url, ydl_opts)
            
            # Find downloaded file
            downloaded_file = None
            for file in os.listdir(self.download_dir):
                if file.startswith(file_id) and file.endswith('.mp4'):
                    downloaded_file = os.path.join(self.download_dir, file)
                    break
            
            if downloaded_file:
                # Get file size information
                file_size = os.path.getsize(downloaded_file) / (1024 * 1024)  # In MB
                self.logger.info(f"Downloaded file: {downloaded_file}, size: {file_size:.2f} MB")
                
                # Rename file to contain video title
                safe_title = re.sub(r'[^\w\-_\. ]', '_', title)
                new_filename = f"{safe_title}_{quality}.mp4"
                new_path = os.path.join(self.download_dir, new_filename)
                
                # If file with such name already exists, add unique identifier
                if os.path.exists(new_path):
                    new_filename = f"{safe_title}_{quality}_{file_id[:8]}.mp4"
                    new_path = os.path.join(self.download_dir, new_filename)
                
                os.rename(downloaded_file, new_path)
                return new_path, new_filename
            
            return None, None
        except Exception as e:
            self.logger.error(f"Error downloading video: {e}")
            return None, None
    
    def _download(self, url: str, options: Dict[str, Any]) -> None:
        """
        Download video (synchronous function for running in a separate thread)
        
        Args:
            url: Video URL
            options: Options for yt-dlp
        """
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
    
    def _list_formats(self, url: str, options: Dict[str, Any]) -> None:
        """
        List available formats for debugging purposes
        
        Args:
            url: Video URL
            options: Options for yt-dlp
        """
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            self.logger.debug(f"Available formats for video {url}:")
            for f in formats:
                format_id = f.get('format_id', 'N/A')
                ext = f.get('ext', 'N/A')
                resolution = f.get('resolution', 'N/A')
                vcodec = f.get('vcodec', 'N/A')
                acodec = f.get('acodec', 'N/A')
                filesize = f.get('filesize', 0)
                filesize_mb = filesize / 1024 / 1024 if filesize else 0
                self.logger.debug(f"ID: {format_id}, Ext: {ext}, Resolution: {resolution}, Vcodec: {vcodec}, Acodec: {acodec}, Size: {filesize_mb:.2f} MB")
    
    async def cleanup_file(self, file_path: str) -> None:
        """
        Delete file after sending
        
        Args:
            file_path: Path to file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")


# Create service instance for use in other modules
youtube_service = YouTubeService() 