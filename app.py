
from flask import Flask, request, render_template
from dotenv import load_dotenv
from pathlib import Path
import os
import requests

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, template_folder="templates")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    message = request.form.get("message", "").strip()

    if not all([name, email, subject, message]):
        return (
            "<h2>Please fill in all fields.</h2>"
            "<a href='/'>Go back</a>"
        ), 400

    api_key = os.getenv("RESEND_API_KEY")
    owner = os.getenv("OWNER_EMAIL") or os.getenv("GMAIL_ADDRESS")

    if not api_key or not owner:
        print("Resend configuration missing.")
        return (
            "<h2>Email settings are missing.</h2>"
            "<a href='/'>Go back</a>"
        ), 500

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Portfolio Contact <onboarding@resend.dev>",
                "to": [owner],
                "reply_to": email,
                "subject": f"Portfolio Contact: {subject}",
                "text": (
                    f"Name: {name}\n"
                    f"Email: {email}\n"
                    f"Subject: {subject}\n\n"
                    f"Message:\n{message}"
                )
            },
            timeout=20
        )

        if response.status_code not in (200, 201):
            print(
                "Resend API error:",
                response.status_code,
                response.text
            )
            return (
                "<h2>Message could not be sent.</h2>"
                "<p>Please try again later.</p>"
                "<a href='/'>Go back</a>"
            ), 500

        print("Contact email sent successfully.")
        return (
            "<h2>Message sent successfully!</h2>"
            "<p>Thank you for contacting me.</p>"
            "<a href='/'>Back to portfolio</a>"
        ), 200

    except requests.RequestException as error:
        print("Email sending error:", repr(error))
        return (
            "<h2>Message could not be sent.</h2>"
            "<p>Please try again later.</p>"
            "<a href='/'>Go back</a>"
        ), 500
