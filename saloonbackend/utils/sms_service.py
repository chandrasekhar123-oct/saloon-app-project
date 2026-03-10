import requests
import json
import os

class SMSService:
    # Get API key from environment variable or set it directly
    # Fast2SMS is popular in India for bulk SMS and OTP
    FAST2SMS_API_KEY = os.environ.get("FAST2SMS_API_KEY") # You can paste your key here
    
    @staticmethod
    def send_otp(phone, otp, salon_name):
        """
        Sends an OTP to the user's phone number.
        """
        message = f"Your OTP for booking at {salon_name} is: {otp}. Thank you for choosing Saloon Essy!"
        
        # If no API key is provided, we print to console (Mock Mode)
        if not SMSService.FAST2SMS_API_KEY or SMSService.FAST2SMS_API_KEY == "YOUR_API_KEY":
            print("\n" + "="*50)
            print("📱 [MOCK SMS SERVICE]")
            print(f"TO: {phone}")
            print(f"MESSAGE: {message}")
            print("="*50 + "\n")
            return True, "Mock SMS sent to console"

        url = "https://www.fast2sms.com/dev/bulkV2"
        
        payload = {
            "route": "otp",
            "variables_values": otp,
            "numbers": phone,
        }
        
        headers = {
            'authorization': SMSService.FAST2SMS_API_KEY,
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"
        }

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            res_data = response.json()
            
            if res_data.get("return"):
                return True, "SMS sent successfully"
            else:
                print(f"❌ SMS API Error: {res_data.get('message')}")
                return False, res_data.get("message")
        except Exception as e:
            print(f"❌ SMS Service Exception: {str(e)}")
            return False, str(e)

    @staticmethod
    def send_booking_confirmation(phone, salon_name, slot_time):
        """
        Sends a generic confirmation message.
        """
        message = f"Booking Confirmed at {salon_name} for {slot_time}. Please visit the shop on time!"
        
        if not SMSService.FAST2SMS_API_KEY or SMSService.FAST2SMS_API_KEY == "YOUR_API_KEY":
            print("\n" + "="*50)
            print("📱 [MOCK SMS SERVICE]")
            print(f"TO: {phone}")
            print(f"MESSAGE: {message}")
            print("="*50 + "\n")
            return True, "Mock SMS sent to console"

        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            "route": "q",
            "message": message,
            "language": "english",
            "numbers": phone,
        }
        
        headers = {'authorization': SMSService.FAST2SMS_API_KEY}

        try:
            response = requests.get(url, params=payload, headers=headers)
            return True, "SMS sent successfully"
        except Exception as e:
            return False, str(e)
