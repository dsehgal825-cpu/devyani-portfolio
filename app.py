
from flask import Flask, request, render_template
from dotenv import load_dotenv
from email.message import EmailMessage
from pathlib import Path
import os
import smtplib
import html

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, template_folder="templates")


@app.route("/api/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not all([name, email, subject, message]):
        return "<h2>Please fill in all fields.</h2><a href='/'>Go back</a>", 400

    gmail = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")
    owner = os.getenv("OWNER_EMAIL") or gmail

    if not gmail or not password or not owner:
        print("Email configuration missing.")
        return "<h2>Email settings are missing.</h2><a href='/'>Go back</a>", 500

    try:
        msg = EmailMessage()
        msg["Subject"] = f"Portfolio Contact: {subject}"
        msg["From"] = gmail
        msg["To"] = owner
        msg["Reply-To"] = email
        msg.set_content(
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}"
        )

        # Timeout: 15 seconds
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=15
        ) as server:
            server.login(gmail, password)
            server.send_message(msg)

        print("Contact email sent successfully.")
        return (
            "<h2>Message sent successfully!</h2>"
            "<p>Thank you for contacting me.</p>"
            "<a href='/'>Back to portfolio</a>"
        ), 200

    except Exception as error:
        print("Email sending error:", repr(error))
        return (
            "<h2>Message could not be sent.</h2>"
            "<p>Please try again later.</p>"
            "<a href='/'>Go back</a>"
        ), 500
