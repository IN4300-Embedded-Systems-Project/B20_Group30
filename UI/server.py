import asyncio
import json
import serial_asyncio
import websockets
import string
from aiohttp import web 
import math

# Load hiker metadata from hikers.json
with open("hikers.json") as f:
    hikers = json.load(f)

# Function to clean and filter bad characters
def clean_data(raw_data):
    # Define allowed characters (e.g., alphanumeric, comma, period, and space)
    allowed_chars = string.ascii_letters + string.digits + ",.- "  # You can extend this set as needed
    
    # Filter out any characters that are not in the allowed set
    cleaned_data = ''.join([char for char in raw_data if char in allowed_chars])

    # Return the cleaned data (if it's valid, or empty if invalid)
    return cleaned_data

# Function to calculate the distance between two GPS points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return distance

# Function to check for outlier latitude and longitude
def is_valid_location(lat, lon, prev_lat, prev_lon, max_distance_km=0.05):
    # Define valid ranges for latitude and longitude
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        # If the change in distance is too large (e.g., greater than 5 km), consider it invalid
        if prev_lat is not None and prev_lon is not None:
            distance = haversine(lat, lon, prev_lat, prev_lon)
            if distance > max_distance_km:
                print(f"Large location change detected: {distance} km")
                return False
        return True
    return False

#  Serve HTML file
# async def handle_html(request):
#     return web.FileResponse('./Home2.html')

# Serve HTML file
async def handle_html(request):
    return web.FileResponse('./Home.html')

# Serve hiker metadata
async def handle_hikers_json(request):
    return web.FileResponse('./hikers.json')

# WebSocket handler (broadcast Arduino data)
async def send_location(websocket):
    while True:
        try:
            data = await serial_queue.get()  # Wait for Arduino data
            await websocket.send(data)  # Forward directly to client
        except Exception as e:
            print(f"Error while sending data via WebSocket: {e}")
            # Continue even if there's an error

# Read Arduino data asynchronously
async def read_serial():
    prev_lat = None
    prev_lon = None
    
    reader, writer = await serial_asyncio.open_serial_connection(
        url='COM7',  # Replace with your Arduino's port (e.g., /dev/ttyUSB0)
        baudrate=115200
    )
    while True:
        try:
            line = await reader.readline()
            raw_data = line.decode().strip()
            
            # Clean the raw data by removing bad characters
            cleaned_data = clean_data(raw_data)
            
            if not cleaned_data:  # If no valid data after cleaning, skip it
                print(f"Received invalid data: {raw_data}")
                continue
            
            # Skip debug lines (if any)
            if cleaned_data.startswith("Sending: "):
                continue
                
            # Parse custom format: "ID,lat,lon,status"
            try:
                hiker_id, lat, lon, status = cleaned_data.split(',')
                lat = float(lat)
                lon = float(lon)

                # Check if the location data is valid and doesn't have a large change
                if not is_valid_location(lat, lon, prev_lat, prev_lon):
                    print(f"Invalid location data received: lat={lat}, lon={lon}")
                    continue  # Skip invalid location data
                
                # Update previous location
                prev_lat, prev_lon = lat, lon

                json_data = json.dumps({
                    "id": hiker_id,
                    "lat": lat,
                    "lon": lon,
                    "status": status.strip()  # Remove whitespace
                })
                await serial_queue.put(json_data)
            except Exception as e:
                print(f"Failed to parse cleaned data: {cleaned_data}. Error: {e}")
        
        except Exception as e:
            print(f"Error while reading serial data: {e}")
            # Continue reading serial data even if there's an error

# Global queue for Arduino data
serial_queue = asyncio.Queue()

# Main program execution
async def main():
    # HTTP Server
    app = web.Application()
    app.router.add_get('/', handle_html)
    app.router.add_get('/hikers.json', handle_hikers_json)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()

    # Start Arduino reader and WebSocket server
    await asyncio.gather(
        read_serial(),
        websockets.serve(send_location, '0.0.0.0', 5001)  # WebSocket for location data
    )

# Run the program
asyncio.run(main())
