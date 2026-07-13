from fastapi import FastAPI
from .schemas import AnalyzeRequest, AnalyzeResponse

app = FastAPI(title="Waji Audio AI", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "audio-ai", "status": "ok"}


@app.post("/v1/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    # 框架阶段不伪造诊断结果；模型接入后替换此实现。
    return AnalyzeResponse(
        recording_id=payload.recording_id,
        status="not_evaluated",
        anomaly_score=None,
        model_version=payload.model_version or "unconfigured",
        notes=["No production model is configured."],
    )
