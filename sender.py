import time
import requests
import json
from api import APIS  # আগের মতো api.py থেকে import

def send_serial_otp(phone, total_otp, delay):
    sent_count = 0
    api_count = len(APIS)

    while sent_count < total_otp:
        for api in APIS:
            if sent_count >= total_otp:
                break

            # phone formatting
            req_phone = phone
            if api.get("add_88"):
                if not req_phone.startswith("+880"):
                    req_phone = "+880" + req_phone.lstrip("0")

            # payload
            payload = api['payload'](req_phone) if api.get('payload') else None
            headers = api.get("headers", {})

            method = api.get("method", "POST").upper()
            try:
                if method == "POST":
                    resp = requests.post(api['url'], json=payload, headers=headers, timeout=15)
                else:
                    resp = requests.get(api['url'], params=payload, headers=headers, timeout=15)

                # Print API status
                print("\n------------------------------------------------------------")
                print(f"📤 API: {api['name']}")
                print(f"URL: {api['url']}")
                print(f"Method: {method}")
                print(f"Payload: {json.dumps(payload, indent=2) if payload else None}")
                print(f"Status Code: {resp.status_code}")
                print(f"Response: {resp.text[:500]}")  # truncate long response
                if resp.status_code in [200, 201]:
                    sent_count += 1
                    print(f"✅ RESULT: SUCCESS | OTP sent: {sent_count}/{total_otp}")
                else:
                    print(f"❌ RESULT: FAILED")

            except requests.exceptions.RequestException as e:
                print(f"🔥 REQUEST ERROR: {e}")
            
            # delay between APIs
            time.sleep(delay)

    print(f"\n🎉 All {total_otp} OTPs processed!")


if __name__ == "__main__":
    phone_input = input("Enter Bangladeshi number (without +88, e.g., 013XXXXXXXX): ").strip()
    total_otp = int(input("How many OTPs to send?: ").strip())
    delay_sec = float(input("Delay between API calls (seconds)?: ").strip())
    send_serial_otp(phone_input, total_otp, delay_sec)
