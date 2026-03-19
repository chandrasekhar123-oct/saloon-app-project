# Security Assessment Document: Saloon Web App (Backend)

## 1. Executive Summary
The Saloon Web App backend (built on Python/Flask and SQLAlchemy) provides APIs for a multi-sided marketplace connecting customers, salon workers, and salon owners. Recent security hardening efforts have significantly improved the application’s posture by mitigating critical Remote Code Execution (RCE) and Sensitive Data Exposure vulnerabilities. However, the application currently lacks defense-in-depth mechanisms against automated attacks (brute-forcing OTPs) and Cross-Site Request Forgery (CSRF). 

**Overall Security Posture:** Moderate to Strong (improving). 

---

## 2. Scope & Methodology
*   **Target Assessed:** `saloonbackend` (Flask Application), `models/` (SQLAlchemy Schema), `routes/` (API Endpoints).
*   **Deployment Assumption:** Cloud-based Virtual Machine or Containerized (Docker) environment communicating with a Mobile App (React Native) and Web Portal.
*   **Methodology:** Static Application Security Testing (SAST) through manual code review and threat modeling aligned with OWASP Top 10 guidelines.

---

## 3. Threat Model
*   **Attack Surfaces:** public-facing REST APIs (`/user`, `/worker`, `/owner`), Authentication endpoints (`/auth`), and file upload handlers (`/upload-photo`).
*   **Threat Actors:** Unauthenticated attackers attempting server compromise, malicious workers attempting vertical privilege escalation, and automated botnets attempting SMS toll fraud or credential stuffing.
*   **Key Attack Vectors:** Brute-forcing the 4-digit numeric OTPs, exploiting overly permissive CORS configurations, and exploiting un-throttled API endpoints.

---

## 4. Vulnerability Findings

### High Severity
*   **Lack of Rate Limiting on OTP and Login Endpoints (OWASP A07:2021 - Identification and Authentication Failures)**
    *   **Description:** The `/auth/send-otp` and `/auth/verify-otp` endpoints do not limit the number of requests a user can make. An attacker can repeatedly call `/send-otp` to rack up Twilio SMS charges (SMS Toll Fraud) or brute-force a mathematically small 4-digit OTP space (10,000 combinations) to hijack a user or worker account.
    *   **Status:** Open

*   **Excessive CORS Configuration (OWASP A05:2021 - Security Misconfiguration)**
    *   **Description:** In `app.py`, `CORS(app)` is declared globally without defining specific origins. This allows any malicious website on the internet to send cross-origin requests to the backend API and read the responses, potentially bypassing CSRF protections (if implemented via cookie).
    *   **Status:** Open

### Medium Severity
*   **Absence of CSRF Protection on State-Changing Web Endpoints (OWASP A01:2021 - Broken Access Control)**
    *   **Description:** While the mobile API relies on JWT or dedicated tokens (assumed), the Web Portal accessed by Owners and Admins utilizes Flask-Login (session cookies). There is currently no `Flask-WTF` or CSRF token mechanism protecting POST routes accessed via the browser, making the portal vulnerable to Cross-Site Request Forgery.
    *   **Status:** Open

*   **Lack of Content Security Policy (CSP)**
    *   **Description:** The Jinja2 templates (e.g., `templates/index.html`) do not implement a robust CSP header. If a Cross-Site Scripting (XSS) vulnerability were introduced in the future, the browser would freely execute the malicious script.
    *   **Status:** Open

### **Previously Remedied Vulnerabilities (For Auditor Reference)**
*   **(Patched) High - Remote Code Execution (RCE):** File upload endpoints previously accepted any file extension. *Mitigation applied: Strict `ALLOWED_EXTENSIONS` whitelisting.*
*   **(Patched) High - Information Disclosure:** OTPs were previously printed directly to stdout in production if Twilio failed. *Mitigation applied: Mock SMS limited exclusively to `current_app.config.get('DEBUG') == True`.*
*   **(Patched) High - Sensitive Data Exposure:** Cryptographic keys were hardcoded in `config.py`. *Mitigation applied: Forced `.env` validation.*

---

## 5. Risk Register

| Risk ID | Vulnerability | Likelihood | Impact | Priority |
| :--- | :--- | :--- | :--- | :--- |
| RSK-01 | OTP Brute-Force / SMS Toll Fraud | High | High | **CRITICAL** |
| RSK-02 | Global CORS Exposure | High | Medium | **HIGH** |
| RSK-03 | Missing CSRF Protection (Web Portal) | Medium | High | **HIGH** |
| RSK-04 | Missing CSP Headers | Low | Medium | **MEDIUM** |

---

## 6. Mitigation Recommendations

### 1. Implement API Rate Limiting (Priority: Critical)
*   **Action:** Install `Flask-Limiter`.
*   **Implementation:** Apply strict rate limits to the `/auth` blueprint. For example, limit `/send-otp` to 3 requests per hour per IP address, and limit `/verify-otp` to 5 failed attempts per hour before locking the account temporarily.

### 2. Restrict CORS (Priority: High)
*   **Action:** Update `app.py` CORS configuration.
*   **Implementation:** Replace `CORS(app)` with an explicit list of allowed origins. Example: `CORS(app, resources={r"/api/*": {"origins": ["https://salooneasy.com", "capacitor://localhost"]}})`

### 3. Add CSRF Protection for Web Forms (Priority: High)
*   **Action:** Install `Flask-WTF`.
*   **Implementation:** Initialize `csrf = CSRFProtect(app)` in `app.py`. Ensure all HTML forms in the Jinja templates include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>`.

---

## 7. Compliance Gaps
*   **OWASP Top 10 (2021):** The application currently deviates from Section A07 (Authentication Failures) due to unprotected OTP routines.
*   **SOC 2 (Security Principle):** The lack of automated rate-limiting and WAF (Web Application Firewall) definitions represents a gap in preventing automated unauthorized access attempts.

---
**Document Revision:** 1.0 | **Author:** Antigravity Security Assessment AI
