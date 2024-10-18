from typing import Protocol, Optional
from abc import ABC, abstractmethod

class VideoSummaryManagerInterface(ABC):
    @abstractmethod
    def list_summaries(self, video_id: str, summary_id: Optional[str] = None) -> Optional[dict]:
        ...
    @abstractmethod
    def create_summary(self, video_id: str, model_name: str = "gpt-35-turbo", sum_len: str = "Long", sum_style: str = "Neutral") -> Optional[dict]:
        ...