APIS = [
    {
        "name": "Chorki",
        "method": "POST",
        "url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en",
        "payload": lambda phone: {"number": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Kirei",
        "method": "POST",
        "url": "https://frontendapi.kireibd.com/api/v2/send-login-otp",
        "payload": lambda phone: {"email": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "DeeptoPlay",
        "method": "POST",
        "url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en",
        "payload": lambda phone: {"number": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Shikho",
        "method": "POST",
        "url": "https://api.shikho.com/auth/v2/send/sms",
        "payload": lambda phone: {
            "auth_type": "signup",
            "phone": phone,
            "type": "student",
            "vendor": "shikho"
        },
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "PBS",
        "method": "POST",
        "url": "https://apialpha.pbs.com.bd/api/OTP/generateOTP",
        "payload": lambda phone: {"otp": "", "userPhone": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "BeautyBooth",
        "method": "POST",
        "url": "https://admin.beautybooth.com.bd/api/v2/auth/register",
        "payload": lambda phone: {"token": 91, "type": "phone", "value": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Paperfly",
        "method": "POST",
        "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php",
        "payload": lambda phone: {
            "full_name": "Md RAHIM",
            "company_name": "Gwewrgre",
            "email_address": "rahim@gmail.com",
            "phone_number": phone
        },
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Apex4U",
        "method": "POST",
        "url": "https://api.apex4u.com/api/auth/login",
        "payload": lambda phone: {"phoneNumber": phone},
        "success": lambda r: r.status_code in [200,201]
    },
]
