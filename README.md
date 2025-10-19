# 🏦 Smart Banking System

A Flask-based web application that provides secure and smart banking features, including user registration, login, ATM lookup, and face image upload for authentication.  
This project demonstrates a practical use of Flask, SQLAlchemy, and SQLite for building a modern banking dashboard system.

---

## 🚀 Features

- 🧑‍💼 User Registration with name, email, password, and initial balance  
- 🔐 Secure Login System with password hashing  
- 💳 User Dashboard showing account balance and profile info  
- 🏧 ATM Locator API for specific pincodes  
- 🖼️ Face Upload System for each user (PNG/JPG/JPEG supported)  
- 🗄️ Database Integration with SQLAlchemy and SQLite  
- 🌐 Modern Frontend (HTML, CSS, JS) resembling real-world banking websites  

---

## ⚙️ Tech Stack

| Layer | Technologies Used |
|:------|:------------------|
| Backend | Python, Flask, SQLAlchemy |
| Database | SQLite (auto-created in `instance/` folder) |
| Frontend | HTML, CSS, JavaScript |
| Security | Werkzeug (password hashing) |
| Others | Flask-CLI commands for DB initialization and seeding |

---

## 🧩 Folder Structure

```
SmartBankingSystem/
│
├── app.py               # Main Flask app with routes
├── models.py            # Database models (User, ATM)
├── rendered.html        # Frontend demo page
├── static/              # CSS, JS, uploaded files
├── templates/           # HTML templates (register, dashboard, etc.)
└── instance/
    └── smartbank.sqlite # Auto-generated database file
```

---

## 🛠️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/smart-banking-system.git
cd smart-banking-system
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install flask flask_sqlalchemy werkzeug
```

### 4️⃣ Initialize the Database
```bash
flask --app app.py init-db
flask --app app.py seed-atms
```

### 5️⃣ Run the Application
```bash
python app.py
```
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser 🚀  

---

## 🔑 Default Admin Access

The application restricts login to the owner account:
```
Email: jamadarshubham123@gmail.com
```
*(You can change this email inside `app.py` for your own use.)*

---

## 🧑‍💻 Author

**Rakesh (Sweetu)**  
Data Science Student | Passionate about Backend Development 💻  

---

## 📝 License
This project is intended for **educational purposes only** and does not represent an actual banking application.
