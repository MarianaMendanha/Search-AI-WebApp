from typing import Optional, Protocol

class VideoUploadManagerInterface(Protocol):
    def upload_by_url(  self, video_name: str, video_url: str,
                        wait_for_index: bool = False, video_description: str = '', privacy: str = 'Private', language: str = 'auto') -> str:
        """
        Uploads a video by URL and starts the video indexing process.
        """
        ...

    def upload_by_file( self, media_path: str, video_name: Optional[str] = None,
                        video_description: str = '',
                        privacy: str = 'Private', partition: str = '', language: str = 'auto') -> str:
        """
        Uploads a local file and starts the video indexing process.
        """
        ...
