from twilio.rest import Client  
import phonenumbers
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_sms(phone_number, message):
    """Send an SMS notification using Twilio."""
    account_sid = 'ACb0db6e91c2fd519d6a3b56748480391e'
    auth_token = 'e547a412ecb96051bb1851946815bf64'
    client = Client(account_sid, auth_token)
    
    try:
        phone_number = f"+{phone_number}"
        parsed_number = phonenumbers.parse(phone_number, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError(f"Invalid phone number: {phone_number}")
        formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)

        client.messages.create(
            body=message,
            from_='+17622167413',
            to=formatted_number
        )
        logging.info(f"Sent SMS to {formatted_number}")
    except Exception as e:
        logging.error(f"Failed to send SMS to {phone_number}: {e}")
