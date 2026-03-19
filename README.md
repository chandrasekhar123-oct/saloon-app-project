# Saloon Essy - Universal Salon Management Ecosystem

Saloon Essy is a comprehensive, multi-platform solution designed to bridge the gap between salon owners, workers, and customers. The ecosystem consists of three main components: a robust backend API, a premium user-facing mobile app, and a specialized worker/owner management application.

## 📱 Project Components

### 1. [Saloon Backend (Flask API)](./saloonbackend/)
The engine of the entire platform, handling authentication, booking logic, and financial management.
- **Tech Stack**: Python, Flask, SQLite, SQLAlchemy.
- **Key Features**: 
    - Google Sign-In Integration (recent implementation).
    - OTP-based authentication via Twilio.
    - Automated worker payout and commission tracking.
    - RESTful API for mobile apps.
    - Admin portal for infrastructure control.

### 2. [Saloon User App (React Native/Expo)](./saloon%20user%20app/saloon-essy-user/)
A premium mobile application for customers to discover and book salon services.
- **Tech Stack**: React Native, Expo, Expo Vector Icons.
- **Key Features**:
    - Real-time salon discovery and search.
    - Multi-service booking workflow.
    - Google and Social login support.
    - Interactive service cards and stylist selection.

### 3. [Saloon Worker/Owner App](./saloon%20worker%20app/)
Dedicated app for staff to manage their schedules and for owners to oversee operations.
- **Tech Stack**: React Native (planned/in-development).
- **Key Features**:
    - Booking management and alerts.
    - Financial insights and balance tracking.
    - Profile management for stylists.

---

## 🛠️ Recent Technical Implementations

### Google Authentication Suite
We recently upgraded the ecosystem with a native Google Identity experience:
- **Technique**: Google Identity Services (GSI) with Account Picker integration.
- **Backend**: Secure JWT verification using `google-auth` library.
- **Data**: Hybrid auth schema in SQLite allowing seamless linking between phone-based and email-based accounts.

### Advanced Financial Module
- **Commission Management**: Real-time calculation of worker earnings based on service price and commission rates.
- **Payout System**: Automated tracking of "Pending Payout" for workers, viewable via the worker dashboard.

---

## 🚀 Installation & Setup

### Backend
1. Navigate to `/saloonbackend`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run migrations: `python migrate_google_auth.py` (and other migration scripts).
4. Start server: `python app.py`.

### User App
1. Navigate to `/saloon user app/saloon-essy-user`.
2. Install dependencies: `npm install`.
3. Start Expo: `npx expo start`.

---

## 📁 Repository Structure
```text
saloon-app-project/
├── saloonbackend/          # Flask API & Admin Templates
├── saloon user app/        # Customer Mobile Application
├── saloon worker app/      # Management Mobile Application
└── README.md               # Main Ecosystem Documentation
```

---
*Created with a focus on premium aesthetics and robust architecture.*
