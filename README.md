# Easepark
This is an Vehicle Management System
# 🚗 Vehicle Parking Management System

A web-based application to manage and streamline the process of parking spot reservations, user management, and parking lot analytics. Built using **Flask**, **SQLite**, and **Bootstrap**, this project provides a modern and responsive interface for both users and administrators.

---

## 📌 Features

### 👤 User Functionality
- **Register/Login:** Secure user authentication using Flask-Login.
- **Book Parking Spot:** Search for available parking lots by location, pin code, or name.
- **Real-time Availability:** View spot availability for each lot before booking.
- **Booking History:** Track all current and past reservations with timestamps.
- **Generate Report:** Get a downloadable summary of all bookings.

### 🛠️ Admin Panel
- **Dashboard View:** View all parking lots, users, and bookings at a glance.
- **Manage Parking Lots & Spots:** Add, edit, or delete lots and their associated spots.
- **Search & Filter:** Quickly search for users or parking lots by ID, name, or lot number.
- **Monitor Activity:** View all active and completed reservations.
- **Analytics Ready:** Structured data to plug into visual dashboards (e.g., charts/tables).

---

## 🧰 Tech Stack

- **Frontend:** HTML5, Bootstrap 5, JavaScript, Jinja2
- **Backend:** Python (Flask Framework)
- **Database:** SQLite3 (lightweight and easy-to-use)
- **Templating:** Jinja2 for dynamic rendering

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/vehicle-parking-management.git
cd vehicle-parking-management



# 2. Install Dependencies
# Make sure you have Python 3.7+ and pip installed:

pip install -r requirements.txt


# 3. Run the App through
python app.py

# Then, open your browser and go to:
http://localhost:5000