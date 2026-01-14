import requests
import random
import time
from apis import APIS


def send_one(phone: str) -> bool:
    """
    Try all APIs randomly.
    Return True if ANY api reports success.
    """
    apis = APIS.copy()
    random.shuffle(apis)

    for api in apis:
        try:
            r = requests.request(
                api["method"],
                api["url"],
                json=api["payload"](phone),
                timeout=10
            )
            if api["success"](r):
                return True
        except:
            pass

    return False


def send_exact(phone: str, total: int, delay: float):
    """
    Send EXACT number of OTP.
    Fail হলে retry করবে অন্য API দিয়ে,
    total এর বেশি কখনো পাঠাবে না।
    """
    sent = 0
    logs = []

    while sent < total:
        ok = send_one(phone)

        if ok:
            sent += 1
            logs.append(f"✅ {sent}/{total} OTP SENT (TRUE)")
        else:
            logs.append(f"❌ {sent+1}/{total} OTP FAILED (FALSE)")

        time.sleep(delay)

    return sent == total, logs
