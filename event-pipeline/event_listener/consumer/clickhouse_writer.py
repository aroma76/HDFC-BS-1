import uuid
from datetime import datetime
from event_listener.config.clickhouse_config import client

def parse_timestamp(ts):
    if not ts:
        return None

    # split timezone
    if "+" in ts:
        main, tz = ts.split("+")
        tz = "+" + tz
    else:
        main = ts
        tz = ""

    # trim nanoseconds → microseconds
    if "." in main:
        base, frac = main.split(".")
        frac = frac[:6]
        main = f"{base}.{frac}"

    return datetime.fromisoformat(main + tz)

def write_event(log_data):
    # Convert timestamp string to datetime
    ts = log_data.get("@timestamp")
    parsed_ts = parse_timestamp(ts)


    row = [
        uuid.uuid4(),
        parsed_ts,
        log_data.get("level"),
        log_data.get("message"),
        log_data.get("serviceName") or "",  # your JSON doesn't have serviceName
        log_data.get("sessionId") or "",
        log_data.get("journeyId") or "",
        log_data.get("journeyName") or "",
        log_data.get("jidAlias") or "",
        log_data.get("clientIp") or "",
        log_data.get("User-Agent") or "",
        log_data.get("requestMethod") or "",
        log_data.get("requestUrl") or "",
        log_data.get("requestHeaders") or "",
        log_data.get("requestBody") or "",
        log_data.get("responseStatus") or "",
        log_data.get("responseHeaders") or "",
        log_data.get("responseBody") or "",
    ]

    client.insert(
        "events_db.events",
        [row],
        column_names=[
            "event_id",
            "timestamp",
            "level",
            "message",
            "service",
            "sessionId",
            "journeyId",
            "journeyName",
            "jidAlias",
            "clientIp",
            "userAgent",
            "requestMethod",
            "requestUrl",
            "requestHeaders",
            "requestBody",
            "responseStatus",
            "responseHeaders",
            "responseBody",
        ],
    )

    print("Inserted into ClickHouse")
