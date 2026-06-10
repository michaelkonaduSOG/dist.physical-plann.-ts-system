# 🏢 Physical Planning Data Collection System

A Django-based web application designed for efficient physical planning data collection, structure registration, payment verification, and administrative approval workflow. The system is built for field officers and planning administrators to manage structure records in a structured and secure way.

---

## 🚀 Features

- Multi-step structure registration workflow (Step 1–4)
- Automatic TS (Tracking System) number generation
- Owner and location data capture (GPS supported)
- Structure evidence photo upload
- Payment capture and receipt upload system
- Administrative approval and rejection workflow
- Permit status tracking (Pending / Approved / Not Permitted)
- Fraud detection (duplicate phone, card, or entry checks)
- Search and detailed structure view
- Edit request system for controlled updates
- Role-based workflow (Collector vs Admin)

---



1. Collector registers structure (Step 1–3)
2. System generates TS number
3. Step 4 captures final structure evidence
4. If payment is required → redirect to payment capture
5. Admin reviews payment
6. Admin approves or rejects structure
7. Permit status updates automatically across system

---



- Backend: Django (Python)
- Database: SQLite
- Frontend: HTML, CSS
- Version Control: Git & GitHub

---

## 📁 Project Structure
accounts/ - User authentication system
core/ - Main TS workflow system
templates/ - HTML views
media/ - Uploaded images (evidence & receipts)



---

## ⚙️ Installation & Setup

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver


 Purpose

This system is designed to simulate a real-world government physical planning unit workflow, improving transparency, data accuracy, and field data collection efficiency.


 Author

Michael Konadu
Computer Science Student | Web Developer





