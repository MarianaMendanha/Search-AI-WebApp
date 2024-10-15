from typing import Protocol, Optional

class VideoContentManagerInterface(Protocol):
    def get_raw_insight(self, video_id: str) -> dict:
        """
        Description
        """
        ...

    def get_prompt(self, video_id: str, promptStyle: str = 'Full', timeout_sec:Optional[int]=None, check_alreay_exists=True) -> Optional[dict]:
        """
        Description
        """
        ...
