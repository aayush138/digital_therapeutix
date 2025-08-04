
# 🌐 Digital Therapeutix

**Digital Therapeutix** is an AI-driven medical platform designed to streamline the diagnosis and personalized phage therapy recommendation for bacterial infections. The system combines clinical expertise with data-driven models to aid healthcare professionals in recommending precise, bacteriophage-based treatments.

---

## 🚀 Features

- 🔐 **Role-Based Authentication** (Admin & Doctor)
- 📬 **Email Verification & Approval Workflow**
- 🔍 **Intelligent Matching Engine**
- 🧬 **FASTA File Analyzer**
- 📊 **Detailed Match Reports**
- 🛡️ **JWT-secured APIs**
- 📁 Admin Interface to manage:
  - Bacteria
  - Phages
  - Manufacturers
  - Phage-Bacteria Interactions
  - Bacteria-Bacteria Interactions
  - Phage-Manufacturer Pricing

---

##  Project Structure

```sh
└── digital_therapeutix/
    ├── README.md
    ├── app
    │   ├── __init__.py
    │   ├── extensions.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   ├── quintx.py
    │   │   └── user.py
    │   ├── routes
    │   │   ├── __init__.py
    │   │   ├── admin.py
    │   │   ├── auth.py
    │   │   ├── dashboard.py
    │   │   └── forms.py
    │   ├── seed
    │   │   ├── bacteria_interactions.csv
    │   │   ├── phage_interactions.csv
    │   │   └── seed_data.py
    │   ├── static
    │   │   ├── css
    │   │   │   └── style.css
    │   │   └── images
    │   │       ├── Forgot_passwordback.png
    │   │       ├── clipboard.svg
    │   │       ├── comingsoon.png
    │   │       ├── doctorhome.png
    │   │       ├── favicon.png
    │   │       ├── help.png
    │   │       ├── logo.png
    │   │       ├── phage-bg.jpg
    │   │       ├── phage-bg.webp
    │   │       ├── profile.jpg
    │   │       ├── success.png
    │   │       └── upload.png
    │   ├── templates
    │   │   ├── admin
    │   │   │   ├── dashboard.html
    │   │   │   ├── sidebar.html
    │   │   │   ├── user.html
    │   │   │   ├── vendor_request.html
    │   │   │   └── verify.html
    │   │   ├── auth
    │   │   │   ├── complete_application.html
    │   │   │   ├── forgot_password.html
    │   │   │   ├── login.html
    │   │   │   ├── reset_password.html
    │   │   │   └── signup.html
    │   │   ├── base.html
    │   │   ├── components
    │   │   │   ├── analysis_report.html
    │   │   │   ├── footer.html
    │   │   │   ├── macros.html
    │   │   │   └── navbar.html
    │   │   └── dashboard
    │   │       ├── cases.html
    │   │       ├── help.html
    │   │       ├── home.html
    │   │       ├── phage_vendors.html
    │   │       ├── result.html
    │   │       └── sidebardoctor.html
    │   └── utils
    │       ├── __init__.py
    │       ├── email.py
    │       ├── helpers.py
    │       ├── matcher
    │       │   ├── matcher.py
    │       │   └── matcher_utils.py
    │       ├── quintx
    │       │   └── quint_analysis.py
    │       └── seed.py
    ├── config.py
    ├── data
    │   └── bacteria_blst
    │       ├── blst.ndb
    │       ├── blst.nhr
    │       ├── blst.nin
    │       ├── blst.not
    │       ├── blst.nsq
    │       ├── blst.ntf
    │       └── blst.nto
    ├── requirements.txt
    └── run.py
```

## ⚙️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: Tailwind CSS, Jinja2
- **Database**: PostgreSQL
- **Deployment**: Gunicorn + Nginx + Systemd
- **Security**: JWT Auth, Role-based Access, SMTP Verification
- **Others**: Python-Dotenv, Flask-Mail, Flask-Migrate

---

## 🧪 Installation (Dev)

1. **Clone Repo**  
   ```bash
   git clone https://github.com/aayush138/digital_therapeutix.git
   cd digital_therapeutix
   ```

2. **Create Virtual Env**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   sudo apt install libpango-1.0-0 libcairo2 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 libffi-dev libxml2 libxslt1-dev
   sudo apt install ncbi-blast+ -y
   ```

4. **Configure .env File**  
   ```env
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DB_URI=your_database_uri
   MAIL_USERNAME=your_email
   MAIL_PASSWORD=your_password
   ...
   ```

5. **Run Server**  
   ```bash
   flask run
   ```

---

## 🧑‍💼 Admin Features

- Approve/Reject Doctor Signups
- Manage Master Data: Bacteria, Phages, Manufacturers
- View Interaction Records
- Track and Edit Match Results

---

## 🧑‍⚕️ Doctor Features

- Signup & Email Verification
- Upload FASTA Files
- View Match Results
- Case Tracking Dashboard

---

## 📄 Environment Variables

Make sure the `.env` file is updated:

```env
SECRET_KEY=...
SQLALCHEMY_DATABASE_URI=...
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=...
MAIL_PASSWORD=...
```

---

## 🛠️ Deployment

```bash
# Start Gunicorn
gunicorn -c gunicorn_config.py run:app

# View logs
sudo journalctl -u digital_therapeutix -f

# Restart service
sudo systemctl restart digital_therapeutix
```

Make sure your `.service` file in `/etc/systemd/system/digital_therapeutix.service` is properly configured.

---

## 🔒 Security Considerations

- Do **not** commit your `.env` file
- Use **strong random** secret keys
- Apply rate limiting and input validation

---

## 📫 Contact

**Digital Therapeutix Team**  
📧 support@digitaltherapeutix.com  
🌐 [https://digitaltherapeutix.com](https://digitaltherapeutix.com)


## License

Digital Therapeutix License

---

**Developed with ❤️ by Nightowl Tech Solutions Pvt. Ltd.**
