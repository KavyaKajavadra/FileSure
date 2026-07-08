"""
FileSure — Main Flask Application
MSME Compliance & Freelancer Financial Checkup Platform
"""

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse

from compliance import (
    BUSINESS_TYPES,
    calculate_upcoming_deadlines,
    get_compliance_summary,
)
from chatbot import get_ai_response

# ── App Configuration ────────────────────────────────────────────────────────

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "filesure-dev-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///filesure.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ── WhatsApp Config ──────────────────────────────────────────────────────────
# Replace with your actual WhatsApp Business number
WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "919999999999")
WHATSAPP_MESSAGE = "Hi FileSure! I'm interested in your compliance services."


# ── Database Models ──────────────────────────────────────────────────────────

class Lead(db.Model):
    """Stores contact form submissions and compliance calendar users."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15), nullable=False)
    business_name = db.Column(db.String(150))
    business_type = db.Column(db.String(50))
    service_interested = db.Column(db.String(100))
    message = db.Column(db.Text)
    source = db.Column(db.String(50), default="contact_form")  # contact_form, compliance_calendar
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Lead {self.name} — {self.phone}>"

import json

class WhatsAppSession(db.Model):
    """Stores active WhatsApp conversations to track history and human handoff state."""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    history = db.Column(db.Text, default="[]")  # Stored as JSON string
    needs_human = db.Column(db.Boolean, default=False)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_history(self):
        return json.loads(self.history)

    def set_history(self, history_list):
        self.history = json.dumps(history_list)


# ── Service Data ─────────────────────────────────────────────────────────────

PLANS = [
    {
        "name": "Starter",
        "price": "999",
        "period": "/month",
        "description": "Perfect for small businesses just getting started with compliance",
        "features": [
            "GST Filing (Monthly GSTR-1 & GSTR-3B)",
            "Compliance Calendar with Reminders",
            "WhatsApp Support",
            "Deadline Alerts via SMS",
        ],
        "highlight": False,
        "cta": "Get Started",
    },
    {
        "name": "Growth",
        "price": "2,499",
        "period": "/month",
        "description": "Complete tax compliance for growing businesses",
        "features": [
            "Everything in Starter",
            "TDS Filing (Quarterly)",
            "Professional Tax Returns",
            "Income Tax Return (Annual)",
            "Dedicated WhatsApp Group",
            "Priority Support",
        ],
        "highlight": True,
        "cta": "Most Popular",
    },
    {
        "name": "Complete",
        "price": "4,999",
        "period": "/month",
        "description": "Full compliance management — you focus on your business",
        "features": [
            "Everything in Growth",
            "ROC Annual Filings (AOC-4, MGT-7)",
            "Director KYC (DIR-3 KYC)",
            "Dedicated Relationship Manager",
            "Monthly Compliance Report",
            "Phone Support",
        ],
        "highlight": False,
        "cta": "Go Complete",
    },
]

ONE_TIME_SERVICES = [
    {"name": "Company / LLP Incorporation", "price": "4,999 – 9,999", "icon": "🏢"},
    {"name": "PAN Application (Individual / Business)", "price": "499", "icon": "🪪"},
    {"name": "TAN Application", "price": "499", "icon": "📋"},
    {"name": "GST Registration", "price": "1,499", "icon": "📦"},
    {"name": "PTEC (Professional Tax — Individuals)", "price": "799", "icon": "💼"},
    {"name": "PTRC (Professional Tax — Employers)", "price": "999", "icon": "🏭"},
    {"name": "Freelancer Financial Checkup", "price": "999", "icon": "🩺"},
    {"name": "Net Worth Certificate", "price": "1,499 – 2,999", "icon": "📜"},
    {"name": "Udyam Registration (MSME)", "price": "499", "icon": "🏗️"},
]

TEAM_MEMBERS = [
    {
        "name": "Kavya",
        "role": "Tech Lead",
        "credential": "Web Developer",
        "description": "Builds the platform, automates workflows, and ensures a seamless digital experience for every client.",
        "initials": "K",
        "color": "#6366f1",
    },
    {
        "name": "Parth",
        "role": "Tax & Compliance",
        "credential": "CA Articleship",
        "description": "Handles GST filing, TDS returns, income tax, and ensures your tax compliance is always on track.",
        "initials": "P",
        "color": "#10b981",
    },
    {
        "name": "Yug",
        "role": "Tax Advisory",
        "credential": "CA Student",
        "description": "Specializes in tax planning, financial advisory, and helping businesses optimize their tax structure.",
        "initials": "Y",
        "color": "#f59e0b",
    },
    {
        "name": "Bhavyy",
        "role": "Company Law & Compliance",
        "credential": "CS Executive",
        "description": "Manages company incorporations, ROC filings, and all corporate law compliance matters.",
        "initials": "B",
        "color": "#ef4444",
    },
    {
        "name": "Nilu",
        "role": "Financial Planning",
        "credential": "BFM Student",
        "description": "Provides financial market insights, investment guidance, and helps clients with banking and loan advisory.",
        "initials": "N",
        "color": "#8b5cf6",
    },
    {
        "name": "Nisarg",
        "role": "Tech & Research",
        "credential": "Engineering Student",
        "description": "Supports platform development, conducts market research, and manages digital presence.",
        "initials": "Ni",
        "color": "#06b6d4",
    },
]

FAQ_ITEMS = [
    {
        "question": "Who is FileSure for?",
        "answer": "FileSure is for small business owners, freelancers, startups, and MSMEs in Mumbai, Thane, and Navi Mumbai who need affordable, reliable compliance and tax filing services.",
    },
    {
        "question": "How is FileSure different from a traditional CA firm?",
        "answer": "We combine professional CA/CS expertise with technology. You get automated reminders, a compliance calendar, digital communication via WhatsApp, and transparent pricing — all at a fraction of what traditional firms charge.",
    },
    {
        "question": "What if I miss a filing deadline?",
        "answer": "That's exactly what we prevent! Our compliance calendar tracks every deadline and sends you reminders well in advance. If you're already late, we'll help you file and minimize penalties.",
    },
    {
        "question": "Can I start with just one service?",
        "answer": "Absolutely. You can start with a single GST filing or a one-time service like GST Registration. No lock-in contracts — upgrade anytime.",
    },
    {
        "question": "Is my financial data safe with FileSure?",
        "answer": "Yes. We follow strict data confidentiality practices. Your financial information is only used for filing purposes and is never shared with third parties.",
    },
    {
        "question": "Do you serve businesses outside Mumbai/Thane?",
        "answer": "Yes! While our core team is based in Mumbai/Thane, all our services are delivered digitally. We can serve businesses across Maharashtra and India.",
    },
]


# ── Template Context Processor ───────────────────────────────────────────────

@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        "whatsapp_link": f"https://wa.me/{WHATSAPP_NUMBER}?text={WHATSAPP_MESSAGE.replace(' ', '%20')}",
        "current_year": datetime.now().year,
    }


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Homepage — hero, pain points, services, how it works, team, compliance tool, FAQ."""
    return render_template(
        "index.html",
        plans=PLANS,
        team=TEAM_MEMBERS,
        faqs=FAQ_ITEMS,
        business_types=BUSINESS_TYPES,
        page_title="Affordable GST, Tax & Compliance Services | Mumbai & Thane",
        page_description="FileSure offers affordable GST filing, ROC compliance, tax advisory, and company incorporation services for MSMEs and freelancers in Mumbai & Thane. Starting at ₹999/month.",
    )


@app.route("/services")
def services():
    """Detailed services page with pricing."""
    return render_template(
        "services.html",
        plans=PLANS,
        one_time_services=ONE_TIME_SERVICES,
        page_title="Services & Pricing",
        page_description="Explore FileSure's compliance packages and one-time services. GST filing, TDS, ROC, company incorporation, and more — all at transparent, affordable prices.",
    )


@app.route("/about")
def about():
    """About page with team profiles."""
    return render_template(
        "about.html",
        team=TEAM_MEMBERS,
        page_title="About Us — Meet the FileSure Team",
        page_description="Meet the FileSure team — young CA, CS, and tech professionals making compliance affordable and hassle-free for MSMEs in Mumbai and Thane.",
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact page with form handling."""
    if request.method == "POST":
        lead = Lead(
            name=request.form.get("name", "").strip(),
            email=request.form.get("email", "").strip(),
            phone=request.form.get("phone", "").strip(),
            business_name=request.form.get("business_name", "").strip(),
            business_type=request.form.get("business_type", "").strip(),
            service_interested=request.form.get("service_interested", "").strip(),
            message=request.form.get("message", "").strip(),
            source="contact_form",
        )
        db.session.add(lead)
        db.session.commit()
        flash("Thank you! We'll reach out to you within 24 hours.", "success")
        return redirect(url_for("contact"))

    return render_template(
        "contact.html",
        business_types=BUSINESS_TYPES,
        plans=PLANS,
        one_time_services=ONE_TIME_SERVICES,
        page_title="Contact Us",
        page_description="Get in touch with FileSure for GST filing, tax advisory, company incorporation, and compliance services in Mumbai and Thane.",
    )


@app.route("/compliance-calendar", methods=["POST"])
def compliance_calendar():
    """Process compliance calendar form and show results."""
    business_type = request.form.get("business_type", "proprietorship")
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()

    # Save as lead
    if name and phone:
        lead = Lead(
            name=name,
            phone=phone,
            business_type=business_type,
            source="compliance_calendar",
        )
        db.session.add(lead)
        db.session.commit()

    # Calculate deadlines
    deadlines = calculate_upcoming_deadlines(business_type)
    summary = get_compliance_summary(business_type)
    business_label = BUSINESS_TYPES.get(business_type, business_type)

    return render_template(
        "calendar_results.html",
        deadlines=deadlines,
        summary=summary,
        business_type=business_label,
        page_title=f"Compliance Calendar — {business_label}",
        page_description=f"Your personalized compliance calendar for {business_label}. See all upcoming GST, TDS, ROC, and tax filing deadlines.",
    )


# ── WhatsApp AI Webhook ──────────────────────────────────────────────────────

@app.route("/whatsapp/webhook", methods=["POST"])
def whatsapp_webhook():
    """Endpoint for Twilio to send incoming WhatsApp messages."""
    incoming_msg = request.values.get("Body", "").strip()
    sender_phone = request.values.get("From", "")

    # Retrieve or create session
    session = WhatsAppSession.query.filter_by(phone_number=sender_phone).first()
    if not session:
        session = WhatsAppSession(phone_number=sender_phone)
        db.session.add(session)
        db.session.commit()
        
    session.last_message_at = datetime.utcnow()
    
    twiml_response = MessagingResponse()

    # If already handed off, do not let AI respond
    if session.needs_human:
        db.session.commit()
        return str(twiml_response) # Send empty response (human will reply)

    # Get conversation history
    history = session.get_history()
    
    # Generate AI response
    ai_result = get_ai_response(incoming_msg, history)
    reply_text = ai_result["text"]
    
    # Update history
    history.append({"role": "user", "parts": [incoming_msg]})
    history.append({"role": "model", "parts": [reply_text]})
    
    # Keep history manageable (last 10 turns = 20 messages)
    if len(history) > 20:
        history = history[-20:]
        
    session.set_history(history)
    
    # Check if handoff was triggered
    if ai_result["handoff"]:
        session.needs_human = True
        
    db.session.commit()
    
    # Send reply via Twilio
    msg = twiml_response.message()
    msg.body(reply_text)
    
    return str(twiml_response)


# ── Database Initialization ──────────────────────────────────────────────────

with app.app_context():
    db.create_all()


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
