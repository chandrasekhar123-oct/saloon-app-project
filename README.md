# Saloon App Project

This repository contains the complete frontend and backend code for the **Saloon App Project**. The project is split into three main components: a backend REST API, a user mobile application, and a worker (salon staff) mobile application.

## 📂 Project Structure

- `saloonbackend/`: A Python **Flask** REST API application that serves as the backend for both mobile apps. It utilizes SQLAlchemy for database management and Flask-Login/Flask-CORS for authentication and cross-origin setup.
- `saloon user app/`: A **React Native (Expo)** mobile application intended for the end-users (clients) to view services, book appointments, etc.
- `saloon worker app/`: A **React Native (Expo)** mobile application designed for the salon staff to manage their work and appointments.

## 🚀 Getting Started

### 1. Backend (`saloonbackend`)

To get the backend up and running, you need Python installed on your system.

```bash
cd saloonbackend
# Create a virtual environment (optional but recommended)
python -m venv venv
# Activate the virtual environment
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
```

### 2. User App (`saloon user app`)

You need Node.js and npm (or yarn) installed.

```bash
cd "saloon user app/saloon-essy-user"
# Install the Node dependencies
npm install

# Start the Expo development server
npm start
```

### 3. Worker App (`saloon worker app`)

Similar to the user app, this is built using React Native and Expo.

```bash
cd "saloon worker app/worker-app"
# Install the Node dependencies
npm install

# Start the Expo development server
npm start
```

## 🛠 Technologies Used
- Backend: Python, Flask, SQLAlchemy
- Frontend (Mobile): React Native, Expo

## 📝 License
Include the project license information here.
