from typing import Literal
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    recording_id: str
    object_uri: str
    device_id: str
    operating_mode: str
    sensor_position: str
    model_version: str | None = None


class AnalyzeResponse(BaseModel):
    recording_id: str
    status: Literal["not_evaluated", "normal", "anomalous"]
    anomaly_score: float | None = Field(default=None, ge=0.0, le=1.0)
    model_version: str
    notes: list[str] = []
