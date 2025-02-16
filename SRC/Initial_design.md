# 2FA Architecture Document

## Overview
This document outlines the architecture of an improved two-factor authentication (2FA) system that enhances security while improving user experience. The proposed system introduces a pattern-based secondary authentication mechanism, similar to Android lock screens, and dynamically changes the pattern on a weekly basis through a mobile application.

## System Components

### 1. Web Authentication System
- **Login Page:** Users enter their standard username and password.
- **Pattern Authentication Prompt:** After password entry, users are prompted to enter a pattern for secondary authentication.
- **Authentication Server:** Verifies user credentials and checks the pattern against the stored hash.

### 2. Mobile Application
- **Pattern Management:** Users will update their authentication pattern weekly.
- **Push Notifications:** The app will remind users to change their pattern weekly.
- **Secure Pattern Storage:** The app stores the updated pattern securely and syncs with the authentication server.

### 3. Backend System
- **User Database:** Stores hashed passwords and encrypted pattern data.
- **Authentication API:** Handles verification of user login requests and pattern validation.
- **Pattern Update Service:** Ensures users update their pattern weekly and notifies them via the mobile app.

## Authentication Flow
1. **User Login Initiation:**
   - The user enters their username and password on the website.
   - Credentials are sent securely to the authentication server.
   
2. **Pattern Authentication:**
   - If credentials are correct, the server requests pattern authentication.
   - The user enters their pattern on the web interface.
   - The entered pattern is hashed and compared to the stored pattern hash.
   
3. **Verification & Access:**
   - If both password and pattern match, access is granted.
   - If incorrect, the user is prompted to retry up to a defined limit.
   
4. **Weekly Pattern Update:**
   - The mobile app prompts the user to update their pattern.
   - Once updated, the new pattern is encrypted and synchronized with the authentication server.

## Security Considerations
- **Pattern Storage:** Patterns are never stored in plaintext; instead, they are hashed and encrypted.
- **Brute Force Protection:** Limits on incorrect attempts to prevent unauthorized access.
- **Multi-Device Synchronization:** The mobile app and authentication server maintain secure synchronization.
- **Secure Communication:** Encrypted channels (TLS) are used for all authentication-related communication.

## Technology Stack
- **Frontend:** React.js for the login page and pattern input UI.
- **Backend:** Node.js with Express.js for authentication handling.
- **Database:** SQLite for storing user credentials and authentication data.
- **Mobile App:** Flutter for cross-platform compatibility.
- **Security:** Argon2 for password hashing, AES for pattern encryption.

## Deployment
- **Cloud-Based Hosting:** AWS EC2 for backend services.
- **Database Hosting:** AWS RDS for secure database storage.


