from contextlib import asynccontextmanager
import math
import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
import boto3
from pydantic import BaseModel

MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")
FEATURE_NAMES = ["age", "workclass", "education_num", "marital_status", "occupation",
                 "relationship", "sex", "capital_gain", "capital_loss", "hours_per_week"]


def download_model():
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    client = boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
    client.download_file(os.environ["ARTIFACT_BUCKET"], MODEL_KEY, MODEL_PATH)
    print("Model da duoc tai xuong tu cloud storage.")


@asynccontextmanager
async def lifespan(app):
    download_model()
    app.state.model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(lifespan=lifespan)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/score")
def score(req: ScoreRequest):
    if len(req.features) != 10 or not all(math.isfinite(x) for x in req.features):
        raise HTTPException(status_code=400, detail="Can dung 10 dac trung so huu han.")
    frame = pd.DataFrame([req.features], columns=FEATURE_NAMES)
    pred = int(app.state.model.predict(frame)[0])
    return {"prediction": pred, "label": "thu_nhap_cao" if pred else "thu_nhap_thap"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
