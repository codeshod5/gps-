# 📍 Real-Time GPS Tracking + ETA Prediction System

A backend-heavy, real-time system that streams GPS data, predicts ETA using machine learning, and updates users via map & notifications. Powered by Kafka, Fastapi, WebSockets, and OpenStreetMap.

---

## 🚀 Features

- ✅ Real-time GPS tracking of drivers  
- ✅ Route-specific map updates (each route shows its own location)  
- ✅ ETA prediction using linear regression  
- ✅ Kafka data streaming for:
  - Frontend tracking  
  - ETA predictions  
  - Notifications  
- ✅ User alert when driver is ~15 minutes away  
- ✅ Stores user login data to Kafka for analytics  
- ✅ Mail notifications (SMS planned)

---

## 🧠 Tech Stack

- **Backend:** Python, Fastapi
- **Streaming:** Apache Kafka  
- **Realtime:** WebSockets  
- **ML:** simple with one feature (Linear Regression)  
- **Frontend:** HTML, JS, Leaflet, OpenStreetMap  
- **Notifications:** fastapi mail

---

## 📂 Kafka Topics Used

| Topic Name          | Description                       |
|---------------------|-----------------------------------|
| `gps_data`          | Raw GPS data from producer        |
| `eta_data`          | ETA prediction results            |
| `send_notification` | User notification payload         |
| `login_logs`        | User login activity logs          |

---


