<table align="center">
  <tr>
    <td align="center" bgcolor="white" style="border-radius:10px;">
      <img src="assets/logo.png" alt="EasePark Logo" width="120" />
    </td>
  </tr>
</table>

<h1 align="center">EasePark 🚗 – Vehicle Parking Management System</h1>

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-black?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)

</div>

---

EasePark is a **Flask-based Vehicle Parking Management System** designed to make parking smarter — from booking and payments to lot administration and data analytics.

🌐 **Live Demo:** [easepark-1.onrender.com](https://easepark-1.onrender.com)

---

## 📸 Gallery

| Home Page | User Dashboard |  Booking History |
|------------|----------------|-----------------|
| ![Home Page](assets/Home_page.png) | ![Dashboard](assets/User_dashboard.png) | ![Booking History](assets/Booking_history.png) |
| Booking via Map | User Statistics | Admin Lot Management |
| ![Map Booking](assets/Booking_through_map.png) | ![User Summary](assets/User_summary_section.png) | ![Admin Dashboard](assets/Admin_dashboard.png) |

---

## ✨ Features

### 👤 User Features
- 🔐 **Authentication:** Secure login via Email/Password or Google OAuth 2.0  
- 🗺️ **Interactive Map:** Real-time lot availability using Leaflet.js  
- ⏱️ **Live Booking:** Reserve and release parking in real time  
- 📩 **Email OTP Verification:** Integrated with Brevo SMTP  
- 💳 **Razorpay Payment Gateway:** Seamless digital payments  
- 📊 **User Dashboard:** Manage bookings, receipts, and personal stats  
- 📈 **Data Visualization:** Personal analytics using Chart.js  

### 🧑‍💼 Admin Features
- 🅿️ Manage multiple parking lots and their spots  
- 👥 Monitor user activities and bookings  
- 📉 Visual dashboard showing occupancy trends and revenue  
- ⚙️ Full CRUD control for lots, users, and pricing  

---

## 🛠 Tech Stack

| Category | Technologies |
|-----------|---------------|
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5, Leaflet.js, Chart.js |
| **Backend** | Python 3.11, Flask, Gunicorn |
| **Database** | PostgreSQL, Redis |
| **Authentication** | Google OAuth 2.0, Flask-Login |
| **Payments** | Razorpay API |
| **Email/Notifications** | Brevo (Sendinblue) SMTP |
| **Deployment** | Docker, Render |

---

## 🧩 System Architecture
```bash
[User] → [Browser] → [Render Host] → [Flask App] → [PostgreSQL]
│
├─> [Redis]
├─> [Razorpay API]
├─> [Brevo SMTP]
└─> [Google OAuth]
```

---

## 🚀 Getting Started (Local Setup)

### 1️⃣ Prerequisites
- Python 3.11+
- PostgreSQL
- Redis
- Google OAuth credentials
- Razorpay Test Keys
- Brevo SMTP key

### 2️⃣ Clone Repo Create Virtual Environment
```bash
git clone https://github.com/your-username/EasePark.git
cd EasePark
```

### 3️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Configure .env File
```bash
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost:5432/easepark_db
REDIS_URL=redis://localhost:6379/0
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_brevo_smtp_key
MAIL_DEFAULT_SENDER=your_email@example.com
```

### 6️⃣ Initialize Database
```bash
flask db init
flask db migrate -m "Initial setup"
flask db upgrade
```

### 7️⃣ Run Application
```bash
flask run
```
```
Visit → http://127.0.0.1:5000
```
---

## ⚙️ Test Accounts

| Role  | Email                                           | Password |
| ----- | ----------------------------------------------- | -------- |
| Admin | [admin@gmail.com](mailto:admin@easepark.com)    | admin123 |
| User  | [user@example.com](mailto:user@example.com)     | user123  |

---

## 💳 Razorpay Test Cards
| Type       | Card Number         | Exp   | CVV | Result    |
| ---------- | ------------------- | ----- | --- | --------- |
| Visa       | 4111 1111 1111 1111 | 12/29 | 123 | ✅ Success |
| Mastercard | 5123 4567 8901 2345 | 12/29 | 123 | ✅ Success |
| Visa       | 4111 1111 1111 1112 | 12/29 | 123 | ❌ Failure |

---

## 📦 Project Structure
```
EasePark/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── controllers/
│   ├── user_routes.py
│   ├── admin_routes.py
│   └── auth_routes.py
├── models/
│   └── user_model.py
├── templates/
│   ├── layout.html
│   ├── user/
│   ├── admin/
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── migrations/
```

---

## ☁ Deployment on Render

- Connect your GitHub repo to Render.

- Create a Web Service and select “Docker”.

- Add PostgreSQL and Redis services.

- Add all environment variables.

- Deploy — Render will automatically build and start your Flask app.

---

## 📄 License

This project is licensed under the MIT License.
See LICENSE
 for more details.
 <p align="center"> Developed with ❤️ by <b>Kshitij Nigam</b> <br> <a href="https://github.com/23f3002142">GitHub</a> • <a href="https://linkedin.com/in/kshitij-nigam-281392287">LinkedIn</a> </p>