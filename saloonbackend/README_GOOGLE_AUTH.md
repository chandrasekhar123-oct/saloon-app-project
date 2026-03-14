# Saloon Essy - Google Authentication Implementation

This document outlines the technical approach and implementation details for the Google Sign-In integration in the Saloon Essy User Portal.

## 🚀 Overview

The implementation uses **Google Identity Services (GSI)** to provide a seamless "One Tap" and account picker experience. It allows users to login or register using their Google accounts without manually entering phone numbers or passwords.

## 🛠️ Technical Techniques Used

### 1. Frontend Integration (GSI SDK)
- **SDK Loading**: We use the asynchronous Google Identity Services script `https://accounts.google.com/gsi/client`.
- **Account Picker**: Instead of a simple redirect, we use `google.accounts.id.prompt()`. This triggers the native Google account picker, providing a premium "human-centric" experience.
- **JWT Handling**: The frontend receives an encoded **JSON Web Token (JWT)** from Google, which is then securely transmitted to the backend via a POST request.

### 2. Backend Security & Verification
- **Token Verification**: We use the `google-auth` Python library to verify the integrity of the JWT.
- **Library**: `google.oauth2.id_token`
- **Technique**: The server verifies the token against Google's public keys to ensure it hasn't been tampered with and was issued specifically for our `GOOGLE_CLIENT_ID`. This prevents "Man-in-the-Middle" attacks.

### 3. Database Strategy (Hybrid Auth)
- **Schema Migration**: We added `email` and `google_id` columns to the `User` model.
- **Flexible Constraints**: The `phone` and `password` fields were made `nullable=True` to support users who exclusively use social login.
- **User Linking**:
    - **By Google ID**: Primary check to retrieve returning Google users.
    - **By Email**: Secondary check to link a Google account to an existing manual registration (if the emails match).
    - **Auto-Provisioning**: If no user exists, a new record is automatically created using Google profile data (name, email, profile picture).

### 4. User Experience (UX)
- **Profile Synchronization**: Automatic extraction of the Google profile picture (`picture` claim in JWT) to populate the user's `profile_image` in our database.
- **Language Support**: Integrated with the existing i18n system to ensure login messages are consistent across English, Telugu, and Hindi.

## 📂 Key Files
- `templates/user_portal/login.html`: Frontend Google button and GSI initialization.
- `routes/user_routes.py`: Backend logic for verification and session management.
- `models/user_model.py`: Updated database structure for social identities.
- `migrate_google_auth.py`: Script used to upgrade the existing database.

## ⚙️ Configuration Required
To activate this in production:
1. Set `GOOGLE_CLIENT_ID` in `config.py`.
2. Add your domain to "Authorized JavaScript origins" in the Google Cloud Console.
