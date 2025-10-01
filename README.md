# 🚗 EasePark – Smart Parking Management System  

> A Flask-based web application that helps users **search, reserve, and manage parking spots** with ease.  
> Deployed live on **Render** and built with **Flask, Bootstrap, SQLite, and Redis**.  

---

## ✨ Features  

### 👤 User Side
- **Secure Authentication** – Login, Signup with password hashing & session management.  
- **User Dashboard** – Central hub with quick actions:  
  - 🔍 **Search Nearby Parking Lots** (by pin code, name, or address).  
  - 🅿️ **Book Parking Spot** with real-time availability.  
  - 📜 **View Booking History** – see past & active reservations.  
  - 📑 **Generate Parking Report** – download or view summaries.  
- **Floating 🚗 Hero Section** – animated car icon for a modern touch.  

### 🛠️ Admin Side
- **User Management** – View & manage registered users.  
- **Parking Lot Management** – Add, edit, and delete parking lots.  
- **Search & Analytics** – Filter by user, lot name, or lot number.  
- **Reports Dashboard** – Track system usage and bookings.  

### ⚡ Technical Highlights
- **Flask + Jinja2** for backend and templating.  
- **Bootstrap 5** for responsive UI.  
- **SQLite** for persistent data storage.  
- **Redis Integration** for caching & rate limiting.  
- **Dockerized** for easy deployment.  
- **Deployed on Render** (both app & Redis instance).  

---

## 🏗️ Tech Stack  

- **Backend:** Flask (Python)  
- **Frontend:** HTML, Jinja2, Bootstrap  
- **Database:** SQLite  
- **Caching / Rate Limiting:** Redis  
- **Containerization:** Docker & Docker Compose  
- **Deployment:** Render  

---

## 📸 Screenshots (add later)
- **Landing Page (🚗 floating hero section)**  
- **User Dashboard**  
- **Booking Spot Page**  
- **Admin Dashboard**  

*(Add screenshots in `/screenshots` folder and link them here)*  

---

## 🚀 Getting Started  

### Prerequisites
- Python 3.10+  
- Redis installed locally or available via Render  
- Docker (optional, for containerized setup)  

### Installation  
```bash
# Clone repo
git clone https://github.com/your-username/easepark.git
cd easepark

# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Locally  
```bash
flask db init
flask db migrate
flask db upgrade
flask run
```

App runs at: **http://127.0.0.1:5000/**  

### Run with Docker  
```bash
docker-compose up --build
```

---

## ☁️ Deployment  

This project is deployed on **Render** with:  
- **Web Service** for Flask app.  
- **Redis Instance** for caching & rate limiting.  

Live Demo 👉 [Your Render URL here]  

---

## 📂 Project Structure  

```
EasePark/
├── templates/       # HTML templates
├── static/          # CSS, JS, assets
├── routes/          # Blueprints (user, admin, auth)
├── models.py        # Database models
├── __init__.py      # App factory
│── migrations/          # DB migrations
│── requirements.txt     # Python dependencies
│── Dockerfile           # Docker build file
│── docker-compose.yml   # Multi-service setup
│── README.md            # Project documentation
```

---

## 🧩 Future Enhancements  
- 📱 Mobile-first redesign with React / Vue frontend.  
- 📍 Google Maps API integration for location-based lot search.  
- 💳 Online payment gateway for prepaid parking.  
- 📊 Advanced admin analytics dashboard.  

---

## 🤝 Contributing  
Pull requests are welcome. For major changes, please open an issue first to discuss what you’d like to change.  

---

## 📜 License  
This project is licensed under the **MIT License** – feel free to use and modify.  

---

🔥 With EasePark, finding and booking a parking spot has never been easier!  
