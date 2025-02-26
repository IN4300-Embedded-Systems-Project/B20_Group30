
# LoRa-Based Hiker Tracking System  
![Project Banner](<Docs/Banner.png>)  
*A decentralized IoT system to track hikers in remote areas with no cellular coverage.*  

---

## Table of Contents  
- [Features](#features)  
- [System Architecture](#system-architecture)  

---

## Features  
- 📍 **Real-Time GPS Tracking**: Monitor hiker locations using LoRa (up to 15 km range).  
- 🆘 **Emergency Alerts**: Hikers can send **HELP/OK** status updates via button triggers.  
- 🗺️ **Interactive Map**: Visualize hiker routes and alerts using OpenStreetMap.  
- 🔋 **Low-Power Design**: Optimized for extended battery life during expeditions.  

---

## System Architecture  
### Hardware Design  
![Hardware Block Diagram](<Docs/Diagram.jpeg>)  

1. **Hiker Device (Transmitter)**:  
   - **Arduino Nano**: Processes GPS data and manages LoRa.  
   - **LoRa SX1278**: Transmits coordinates and status.  
   - **NEO-6M GPS**: Fetches latitude/longitude.  
   - **Li-Ion Battery**: Powers the device for 48+ hours.  

2. **Base Station (Receiver)**:  
   - **Arduino Nano**: Receives and forwards data to PC.  
   - **LoRa SX1278**: Listens for hiker transmissions.  
   - **PC**: Runs Python backend and React frontend.

![Circuit Diagram](<Docs/Block Diagram.png>)  

### Software Workflow  

```mermaid
graph TD
  A[Hiker Device] -->|LoRa| B(Base Station)
  B -->|Serial| C(Python Backend)
  C -->|WebSocket| D(React Frontend)
  D --> E[Live Map]
  D --> F[HELP Alerts]
