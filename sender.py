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

            # 🔑 GET / POST auto
            if api["method"].upper() == "GET":
                r = requests.get(
                    api["url"] + (payload if isinstance(payload, str) else ""),
                    params=None if isinstance(payload, str) else payload,
                    timeout=10
                )
            else:  # POST
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
