from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Updates.updates import Flight, get_all_flights, get_flight, update_flight_status

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/flights")
async def get_all_flights_endpoint():
    try:
        flights = get_all_flights()
        return flights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/flights/{flight_id}")
async def get_flight_endpoint(flight_id: str):
    try:
        flight = get_flight(flight_id)
        return flight
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/flights/{flight_id}")
async def update_flight_status_endpoint(flight_id: str, flight: Flight):
    try:
        updated_flight = update_flight_status(flight_id, flight.status)
        return updated_flight
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)