<!--<div align="center"><img src="path/to/your/logo.png" alt="EasePark Logo" width="150" /></div>--><h1 align="center">EasePark - Vehicle Parking Management System</h1><div align="center"><!-- Fixed Badge URLs --><img src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.11-blue%3Fstyle%3Dfor-the-badge%26logo%3Dpython%26logoColor%3Dwhite" alt="Python 3.11"><img src="https://www.google.com/search?q=https://img.shields.io/badge/Flask-black%3Fstyle%3Dfor-the-badge%26logo%3Dflask%26logoColor%3Dwhite" alt="Flask"><img src="https://www.google.com/search?q=https://img.shields.io/badge/PostgreSQL-316192%3Fstyle%3Dfor-the-badge%26logo%3Dpostgresql%26logoColor%3Dwhite" alt="PostgreSQL"><img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis"><img src="https://www.google.com/search?q=https://img.shields.io/badge/Bootstrap-5.3-7952B3%3Fstyle%3Dfor-the-badge%26logo%3Dbootstrap%26logoColor%3Dwhite" alt="Bootstrap"><img src="https://www.google.com/search?q=https://img.shields.io/badge/Render-46E3B7%3Fstyle%3Dfor-the-badge%26logo%3Drender%26logoColor%3Dblack" alt="Render"></div>EasePark is a full-stack web application designed to streamline the process of finding and booking parking spots. It provides a seamless user experience with real-time map integration, secure payments, and a comprehensive user dashboard. The admin panel allows for easy management of parking lots, spots, and user data.Live Demo: https://easepark-1.onrender.com📸 Gallery<table width="100%"><tr><td align="center"><b>Home Page</b></td><td align="center"><b>User Dashboard</b></td><td align="center"><b>Interactive Map Booking</b></td></tr><tr><!-- Make sure to upload these images to an 'assets' folder in your repo --><td><img src="assets/Home_page.jpg" alt="Home Page" /></td><td><img src="assets/User_dashboard.png" alt="User Dashboard" /></td><td><img src="assets/Booking_through_map.jpg" alt="Booking through map" /></td></tr><tr><td align="center"><b>Booking History</b></td><td align="center"><b>User Statistics</b></td><td align="center"><b>Admin Lot Management</b></td></tr><tr><td><img src="assets/Booking_history.png" alt="Booking History Page" /></td><td><img src="assets/User_summary_section.png" alt="User summary and statistics" /></td><td><img src="assets/Admin_dashboard.png" alt="Admin Dashboard for Lot Management" /></td></tr><tr><td align="center"><b>Admin Statistics</b></td><td align="center"></td><td align="center"></td></tr><tr><td><img src="assets/Admin_summary_section.png" alt="Admin Statistics Dashboard" /></td><td></td><td></td></tr></table>✨ FeaturesUser FeaturesAuthentication: Secure login/registration using Google OAuth 2.0 or standard email/password.Interactive Map: Find available parking lots using an interactive Leaflet.js map, centered on the user's geolocation.Real-time Booking: Select a parking spot and book it in real-time.OTP Verification: SMTP email integration (via Brevo) sends a one-time password to confirm reservations.Payment Gateway: Securely pay for parking sessions using the Razorpay API.User Dashboard: A comprehensive dashboard showing active bookings, booking history, and profile management.Data Visualization: View personal parking statistics (total spending, duration) with responsive charts using Chart.js.Admin FeaturesLot Management: Create, view, update, and delete parking lots.Spot Visualization: A visual grid-based overview of all spots in a lot, showing 'Available' vs. 'Occupied' status.User Management: View and manage all registered users.Admin Dashboard: A summary dashboard showing system-wide statistics (occupancy, registrations, usage trends).🛠️ Tech Stack & ArchitectureCategoryTechnologyFrontendHTML5, CSS3, JavaScript, Bootstrap 5, Leaflet.js, Chart.jsBackendPython 3.11, Flask, GunicornDatabasePostgreSQL (Primary DB), Redis (Rate Limiting)AuthenticationGoogle OAuth 2.0, Flask-Login, Werkzeug (Password Hashing)PaymentsRazorpay APINotificationsSMTP (Brevo)DeploymentDocker, RenderSystem ArchitectureThe application uses a monolithic architecture with Flask serving as the backend. It connects to a PostgreSQL database for persistent storage and Redis for rate-limiting. External APIs (Google, Razorpay, Brevo) are used for authentication, payments, and email notifications.[User] --> [Web Browser] --> [Render] --> [Docker Container]
                                              |
                                              v
           [Gunicorn] --> [Flask App] --+--> [PostgreSQL] (Data)
                                      |
                                      +--> [Redis] (Cache, Tasks)
                                      |
                                      +--> [Google OAuth API]
                                      |
                                      +--> [Razorpay API]
                                      |
                                      +--> [Brevo (SMTP) API]
🚀 Getting Started (Local Setup)Follow these instructions to get the project running on your local machine.1. PrerequisitesPython 3.11+PostgreSQLRedisA Google Cloud Platform project for OAuthA Razorpay account for API keysA Brevo (formerly Sendinblue) account for SMTP2. Clone the Repositorygit clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
3. Set Up a Virtual Environment# Create the virtual environment
python -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate
4. Install Dependenciespip install -r requirements.txt
5. Configure Environment VariablesCreate a .env file in the root directory and fill it with your credentials. Use the structure below (based on your project's .env file).# Flask App
SECRET_KEY=a_very_strong_random_secret_key
FLASK_APP=app.py
FLASK_DEBUG=True
BASE_URL=[http://127.0.0.1:5000](http://127.0.0.1:5000)

# Database
SQLALCHEMY_DATABASE_URI="postgresql://username:password@localhost:5432/easepark_db"
REDIS_URL="redis://localhost:6379/0"

# Google OAuth 2.0
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Razorpay API (Test Mode)
RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_key_secret

# Brevo (Sendinblue) SMTP
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_brevo_email@example.com
MAIL_PASSWORD=your_brevo_smtp_key
MAIL_DEFAULT_SENDER=your-name@your-domain.com
BREVO_API_KEY=your_brevo_api_key
6. Set Up the Database(Assuming you are using Flask-Migrate)# Initialize the migration folder (only first time)
flask db init

# Create the initial migration
flask db migrate -m "Initial database setup"

# Apply the migration to the database
flask db upgrade
7. Run the Applicationflask run
The application will be available at http://127.0.0.1:5000.⚙️ Usage & Test AccountsYou can use the following credentials to test the application in your local environment.Test CredentialsRoleEmailPasswordAdminadmin@easepark.comadmin123Useruser@example.comuser123Razorpay Test ModeTo test the payment flow, use the Razorpay Test Mode keys in your .env file and one of the following test cards at checkout. (Yes, these are the official test cards and will work exactly as described).Card TypeCard NumberExpiryCVVVisa (Success)4111 1111 1111 111112/29123Mastercard (Success)5123 4567 8901 234512/29123Visa (Failure)4111 1111 1111 111212/29123Mastercard (Failure)5123 4567 8901 234612/29123📦 Project Structureeasepark/
├── app.py          # Main Flask application factory
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker build instructions
├── docker-compose.yaml # Docker services
├── .env              # (GitIgnored) Stores all secrets
├── controllers/      # Flask Blueprints / Routes
│   ├── user_routes.py
│   ├── admin_routes.py
│   └── auth_routes.py
├── models/           # SQLAlchemy models
│   └── user_model.py
├── templates/        # Jinja2 HTML templates
│   ├── layout.html
│   ├── user/
│   │   ├── dashboard.html
│   │   ├── book_map.html
│   │   └── summary.html
│   └── admin/
│       └── dashboard.html
├── static/           # CSS, JS, Images
│   ├── css/
│   └── js/
└── migrations/       # Flask-Migrate files
☁️ DeploymentThis application is configured for easy deployment on Render using Docker.Connect your GitHub repository to Render.Create a new "Web Service" and point it to this repository.Set the Runtime to "Docker". Render will automatically detect your docker-compose.yaml.Add your PostgreSQL and Redis services on Render.Copy the database and Redis URLs from your new services.Go to the "Environment" tab for your web service and add all the secret keys from your local .env file, updating the SQLALCHEMY_DATABASE_URI and REDIS_URL with your Render service URLs.Deploy! Render will build your Docker image and launch your application.📄 LicenseThis project is licensed under the MIT License - see the LICENSE.md file for details.<p align="center">Developed by <b>Kshitij Nigam</b> - <a href="https://www.google.com/search?q=https://github.com/23f3002142">GitHub</a> | <a href="https://www.google.com/search?q=https://www.linkedin.com/in/kshitij-nigam-281392287">LinkedIn</a></p>