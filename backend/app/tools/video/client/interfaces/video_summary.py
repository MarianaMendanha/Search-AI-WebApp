from typing import Protocol, Optional

class VideoSummaryManagerInterface(Protocol):
    def list_summaries(self, video_id: str, summary_id: Optional[str] = None) -> Optional[dict]:
        ...
    def create_summary(self, video_id: str, model_name: Optional[str] = "gpt-35-turbo", sum_len: Optional[str] = "Long", sum_style: Optional[str] = "Neutral") -> Optional[dict]:
        ...