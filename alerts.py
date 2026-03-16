import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_slack_alert(message: str) -> bool:
    if not SLACK_WEBHOOK_URL:
        return False
    resp = requests.post(SLACK_WEBHOOK_URL, json={"text": message}, timeout=10)
    return resp.status_code == 200


def check_and_alert(overdue_count: int, low_stock_parts: list):
    messages = []

    if overdue_count > 0:
        messages.append(
            f":warning: *ERP Dashboard Alert*\n"
            f"{overdue_count} work order(s) are past their due date."
        )

    if low_stock_parts:
        part_list = "\n".join(f"  - {p}" for p in low_stock_parts[:10])
        messages.append(
            f":warning: *ERP Dashboard Alert*\n"
            f"{len(low_stock_parts)} part(s) below reorder point:\n{part_list}"
        )

    for msg in messages:
        send_slack_alert(msg)
