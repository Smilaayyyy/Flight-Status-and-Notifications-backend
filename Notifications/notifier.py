import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import pika
import json
import os
import time
import logging
from email_service import send_email
from sms_service import send_sms

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

flight_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1laHvbrccUX7sIO0ireJ83xcUX3otTzCyiRJyysQ5z1Q/edit#gid=1244431764')
user_sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1RrdpN1s8xLxk65atchfg3NIhg5hgDzQw7EuJL9H0Q0g/edit#gid=0')

flight_worksheet = flight_sheet.get_worksheet(0)
user_worksheet = user_sheet.get_worksheet(0)

def read_sheet_data(worksheet):
    """Read data from Google Sheets worksheet and return as DataFrame."""
    try:
        records = worksheet.get_all_records()
        logging.info(f"Read data from {worksheet.title}")
        return pd.DataFrame(records)
    except Exception as e:
        logging.error(f"Failed to read data from {worksheet.title}: {e}")
        return pd.DataFrame()

def publish_to_queue(channel, flight_data):
    """Publish flight data to RabbitMQ queue."""
    try:
        channel.basic_publish(
            exchange='flight_status_exchange',
            routing_key='flight_status',
            body=json.dumps(flight_data)
        )
        logging.info(f"Published to queue: {flight_data}")
    except Exception as e:
        logging.error(f"Failed to publish to queue: {e}")

def notify_users(users, flight_data):
    """Notify users about flight status changes."""
    for user in users:
        if user['flight_id'] == flight_data['flight_id']:
            subject = f"Flight {flight_data['flight_id']} Status Update"
            body = f"The status of your flight {flight_data['flight_id']} has changed to {flight_data['status']}."
            send_email(user['Email'], subject, body)
            send_sms(user['Phone No'], body)
            logging.info(f"Notified user {user['Email']} and {user['Phone No']}")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='flight_status_exchange', exchange_type='direct')

    previous_flight_data = None

    while True:
        # Read data from Google Sheets
        flight_data_df = read_sheet_data(flight_worksheet)
        user_data_df = read_sheet_data(user_worksheet)
        
        if flight_data_df.empty or user_data_df.empty:
            logging.error("One of the sheets is empty or could not be read.")
            time.sleep(60)
            continue

        flight_data_list = flight_data_df.to_dict(orient='records')
        user_data_list = user_data_df.to_dict(orient='records')

        if previous_flight_data is None:
            previous_flight_data = flight_data_list

        # Compare new flight data with previous data
        for flight_data in flight_data_list:
            for prev_flight_data in previous_flight_data:
                if flight_data['flight_id'] == prev_flight_data['flight_id'] and flight_data['status'] != prev_flight_data['status']:
                    logging.info(f"Change detected in flight {flight_data['flight_id']} status")
                    publish_to_queue(channel, flight_data)
                    notify_users(user_data_list, flight_data)

        previous_flight_data = flight_data_list
        time.sleep(60)  

if __name__ == '__main__':
    main()