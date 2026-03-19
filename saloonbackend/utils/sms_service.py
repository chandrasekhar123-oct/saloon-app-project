import os
from twilio.rest import Client
from flask import current_app

class SMSService:
    @staticmethod
    def get_twilio_client():
        account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
        
        if not account_sid or account_sid == 'YOUR_ACCOUNT_SID':
            return None
        
        try:
            return Client(account_sid, auth_token)
        except Exception as e:
            print(f"❌ Twilio Client Error: {str(e)}")
            return None

    @staticmethod
    def send_otp(phone, otp, salon_name):
        """
        Sends an OTP to the user's phone number using Twilio.
        """
        message_body = f"Your OTP for booking at {salon_name} is: {otp}. Thank you for choosing Saloon Essy!"
        return SMSService._send_twilio_sms(phone, message_body)

    @staticmethod
    def send_booking_confirmation(phone, salon_name, slot_time):
        """
        Sends a generic confirmation message using Twilio.
        """
        message_body = f"Booking Confirmed at {salon_name} for {slot_time}. Please visit the shop on time!"
        return SMSService._send_twilio_sms(phone, message_body)

    @staticmethod
    def _send_twilio_sms(phone, body):
        client = SMSService.get_twilio_client()
        from_number = current_app.config.get('TWILIO_PHONE_NUMBER')

        if not client or not from_number or from_number == 'YOUR_TWILIO_PHONE_NUMBER':
            if current_app.config.get('DEBUG'):
                print("\n" + "="*50)
                print("📱 [MOCK SMS SERVICE - TWILIO NOT CONFIGURED]")
                print("⚠️  WARNING: Running in development mode. Secrets printed to console.")
                print(f"TO: {phone}")
                print(f"MESSAGE: {body}")
                print("="*50 + "\n")
                return True, "Mock SMS sent to console"
            else:
                print("❌ Twilio SMS Error: SMS Service is not configured for production environment.")
                return False, "SMS Service is not configured. Please contact support."

        try:
            # Ensure phone number is in E.164 format (starts with +)
            if not phone.startswith('+'):
                # Assuming Indian numbers if no prefix, prefix with +91
                if len(phone) == 10:
                    phone = "+91" + phone
                else:
                    # Generic fallback if it's already a full number but missing +
                    phone = "+" + phone

            message = client.messages.create(
                body=body,
                from_=from_number,
                to=phone
            )
            print(f"✅ Twilio SMS Sent: {message.sid}")
            return True, f"SMS sent successfully: {message.sid}"
        except Exception as e:
            print(f"❌ Twilio SMS Error: {str(e)}")
            return False, str(e)
