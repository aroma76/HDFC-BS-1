import json
import os
import shutil
from event_listener.config.redis_config import redis_client, QUEUE_NAME
from .clickhouse_writer import write_event

IN_PROGRESS_DIR = "logs/in_progress"
SUCCESS_DIR = "logs/success"
FAILURE_DIR = "logs/failure"

print("Consumer started...")

while True:
    _, event = redis_client.brpop(QUEUE_NAME)
    data = json.loads(event)

    filename = data["filename"]
    log_data = data["log"]

    try:
        write_event(log_data)
        redis_client.lpush("success_logs", event)

    except Exception:
        redis_client.lpush("failure_logs", event)
        redis_client.incr(f"{filename}:failure_count")

    # Increment processed count
    redis_client.incr(f"{filename}:processed_logs")

    total_logs = int(redis_client.get(f"{filename}:total_logs"))
    processed_logs = int(redis_client.get(f"{filename}:processed_logs"))

    if processed_logs == total_logs:

        source = os.path.join(IN_PROGRESS_DIR, filename)

        failure_count = redis_client.get(f"{filename}:failure_count")
        failure_count = int(failure_count) if failure_count else 0

        if failure_count == 0:
            shutil.move(source, os.path.join(SUCCESS_DIR, filename))
            print(f"{filename} moved to SUCCESS")
        else:
            shutil.move(source, os.path.join(FAILURE_DIR, filename))
            print(f"{filename} moved to FAILURE")

        # Cleanup
        redis_client.delete(f"{filename}:total_logs")
        redis_client.delete(f"{filename}:processed_logs")
        redis_client.delete(f"{filename}:failure_count")