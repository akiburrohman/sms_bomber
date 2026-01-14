import requests, random, time
from apis import APIS

def send_one(phone):
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
                return True, api["name"]
        except:
            pass

    return False, None


def send_exact(phone, total, delay):
    sent = 0
    logs = []

    while sent < total:
        ok, api = send_one(phone)
        if ok:
            sent += 1
            logs.append(f"✅ {sent}/{total} via {api}")
        else:
            logs.append("❌ All API failed")

        time.sleep(delay)

    return sent == total, logs
