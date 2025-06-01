import os
import requests
from dotenv import load_dotenv
load_dotenv()  
import time



def send_sms(number, message):
    url = os.getenv("BULKSMS_API_URL")
    api_key = os.getenv("BULKSMS_API_KEY")
    sender_id = os.getenv("BULKSMS_SENDER_ID")

    payload = {
        'api_key': api_key,
        'senderid': sender_id,
        'number': number,
        'message': message,
        'type': 'text'
    }


    try:
        response = requests.post(url, data=payload, timeout=10)
        response_data = response.json()
        response_code = str(response_data.get("response_code", ""))

        if response_code == "202":
            return {"status": "SUCCESS", "data": response_data}
        else:
            return {"status": "FAILED", "data": response_data}

    except Exception as e:
        return {"status": "ERROR", "msg": str(e)}


def normalize_number(number):
    """Ensure number starts with 8801..."""
    number = number.strip().replace(' ', '')
    if number.startswith('8801'):
        return number
    elif number.startswith('01'):
        return '88' + number
    elif number.startswith('+8801'):
        return number.replace('+', '')
    else:
        return '8801' + number[-9:]  # fallback




def get_sms_balance():
    url = os.getenv("BULKSMS_BALANCE_URL")
    api_key = os.getenv("BULKSMS_API_KEY")

    if not api_key:
        return {
            "balance": "Unavailable",
            "sms_limit": 0,
            "error": "API key not found. Please check .env and load_dotenv()."
        }


    try:
        response = requests.post(url, data={'api_key': api_key})

        data = response.json()
        balance = float(data.get("balance", 0))
        sms_cost = 0.35

        sms_limit = int(balance // sms_cost)

        return {
            "balance": balance,
            "sms_limit": sms_limit
        }

    except Exception as e:
        return {
            "balance": "Unavailable",
            "sms_limit": 0,
            "error": str(e)
        }



