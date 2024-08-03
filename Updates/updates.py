# updates/updates.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel
from fastapi import HTTPException
import logging

class Flight(BaseModel):
    flight_id: str
    status: str

class GoogleSheetsClient:
    def __init__(self, creds_file: str, scope: list):
        self.scope = scope
        self.creds_file = creds_file
        self.client = self._authorize()
        
    def _authorize(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.creds_file, self.scope)
        return gspread.authorize(creds)
    
    def get_worksheet(self, sheet_id: str, worksheet_name: str):
        return self.client.open_by_key(sheet_id).worksheet(worksheet_name)

class FlightDataManager:
    def __init__(self, sheets_client: GoogleSheetsClient, sheet_id: str, worksheet_name: str):
        self.worksheet = sheets_client.get_worksheet(sheet_id, worksheet_name)

    def get_flight_data(self):
        return self.worksheet.get_all_records()

    def update_flight_status(self, flight_id: str, status: str):
        flights = self.get_flight_data()
        flight_index = next((index for (index, f) in enumerate(flights) if f['flight_id'] == flight_id), None)
        
        if flight_index is None:
            raise HTTPException(status_code=404, detail="Flight not found")

        cell = self.worksheet.find(flight_id)
        self.worksheet.update_cell(cell.row, 4, status)  
        flights[flight_index]['status'] = status
        return flights[flight_index]

# Instantiate GoogleSheetsClient with necessary credentials and scope
sheets_client = GoogleSheetsClient(creds_file='credentials.json', scope=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
flight_data_manager = FlightDataManager(sheets_client, sheet_id='1laHvbrccUX7sIO0ireJ83xcUX3otTzCyiRJyysQ5z1Q', worksheet_name='flights')

def get_all_flights():
    return flight_data_manager.get_flight_data()

def get_flight(flight_id: str):
    flights = flight_data_manager.get_flight_data()
    flight = next((flight for flight in flights if flight['flight_id'] == flight_id), None)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

def update_flight_status(flight_id: str, status: str):
    return flight_data_manager.update_flight_status(flight_id, status)
