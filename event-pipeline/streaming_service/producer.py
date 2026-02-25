import redis
from streaming_service import config

r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)

INCOMING_BUFFER = "incoming_buffer"
MAIN_QUEUE = config.QUEUE_NAME
FAILURE_QUEUE = "failure_logs"

def run_producer():
    print("Producer worker started...")

    while True:
        try:
            # Blocking pop (waits until log arrives)
            _, log = r.brpop(INCOMING_BUFFER)

            if log:
                r.lpush(MAIN_QUEUE, log)
                print("Moved log to main_queue")

        except Exception as e:
            print("Producer error:", str(e))

if __name__ == "__main__":
    run_producer()