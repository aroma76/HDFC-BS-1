from fastapi import FastAPI, UploadFile, File
from typing import List
import redis
import json
import os

app = FastAPI()
redis_client = redis.Redis(host="localhost", port=6379, db=0)

IN_PROGRESS_DIR = "logs/in_progress"
os.makedirs(IN_PROGRESS_DIR, exist_ok=True)


@app.post("/upload-log-files/")
async def upload_log_files(files: List[UploadFile] = File(...)):

    for file in files:
        file_path = os.path.join(IN_PROGRESS_DIR, file.filename)

        # 1️⃣ Save uploaded file first
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 2️⃣ Now read saved file
        with open(file_path, "r") as f:
            lines = [line for line in f if line.strip()]

        total_logs = len(lines)

        # 3️⃣ Store counters in Redis
        redis_client.set(f"{file.filename}:total_logs", total_logs)
        redis_client.set(f"{file.filename}:processed_logs", 0)

        # 4️⃣ Push each log to Redis queue
        for line in lines:
            payload = {
                "filename": file.filename,
                "log": json.loads(line)
            }
            redis_client.lpush("incoming_buffer", json.dumps(payload))

    return {"status": "saved_and_queued"}