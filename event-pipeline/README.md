#  Event Pipeline (API → Redis → ClickHouse)

A production-style log ingestion pipeline using:

-  FastAPI (Log ingestion API)
-  Redis (Buffer + Queue + Status Tracking)
-  Producer Worker (Queue mover)
-  Consumer Worker (Processor)
-  ClickHouse (Storage)
-  Docker Compose (Infrastructure)

#  Project Structure
event-pipeline/
│
├── docker-compose.yml
│
├── api/
│   └── main.py
│
├── streaming_service/
│   ├── producer.py
│
├── event_listener/
│   ├── config/
│   │   ├── clickhouse_config.py
│   │   └── redis_config.py
│   │
│   └── consumer/
│       ├── clickhouse_writer.py
│       └── consumer.py
│
└── venv/

# Architecture
Client (Postman / Swagger)
        ↓
FastAPI (upload endpoint)
        ↓
Redis → incoming_buffer
        ↓
Producer Worker (continuous)
        ↓
Redis → main_queue
        ↓
Consumer Worker (continuous)
        ↓
ClickHouse
        ↓
Redis → success_logs / failure_logs

# First Time Setup

##  Start Infrastructure
docker compose up -d

Check containers:
docker ps

You should see:
redis_server
clickhouse_server


# 2️⃣ Create ClickHouse Table (Only Once)
docker exec -it clickhouse_server clickhouse-client --user default --password clickhouse


Inside ClickHouse:
CREATE DATABASE IF NOT EXISTS events_db;

CREATE TABLE IF NOT EXISTS events_db.events
(
    event_id UUID,
    timestamp DateTime64(6),
    level String,
    message String,
    service String,
    sessionId String,
    journeyId String,
    journeyName String,
    jidAlias String,
    clientIp String,
    userAgent String,
    requestMethod String,
    requestUrl String,
    requestHeaders String,
    requestBody String,
    responseStatus String,
    responseHeaders String,
    responseBody String
)
ENGINE = MergeTree()
PARTITION BY toDate(timestamp)
ORDER BY (timestamp);

exit
# 🔹 3️⃣ Setup Python Environment

Activate venv:
.\venv\Scripts\activate

Install dependencies:
pip install fastapi uvicorn redis clickhouse-connect python-multipart

# 4️⃣ Run The System (Every Time)

## Terminal 1 → Producer Worker
python -m streaming_service.producer
Expected:
Producer worker started...

## Terminal 2 → Consumer Worker
python -m event_listener.consumer.consumer
Expected:
Consumer started...

## Terminal 3 → Start API
uvicorn api.main:app --reload

Open Swagger:
http://127.0.0.1:8000/docs


# 5️⃣ Upload Log Files (JSONL Format)
POST /upload-log-files/
Upload:
- sample1.log
- sample2.log
- sample3.log

#  6️⃣ Check Processing Status

## Check total success / failure:
GET /logs/status/

# 7️⃣ Verify Data in ClickHouse
docker exec -it clickhouse_server clickhouse-client 
Then:
SELECT count() FROM events_db.events;

# 8️⃣ Useful Redis Commands

Enter Redis:


docker exec -it redis_server redis-cli

Check queue sizes:

LLEN incoming_buffer
LLEN main_queue
LLEN success_logs
LLEN failure_logs

Clear all queues (reset test):

DEL incoming_buffer
DEL main_queue
DEL success_logs
DEL failure_logs



