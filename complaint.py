from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Complaint(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    ticket_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    title = db.Column(
        db.String(200)
    )

    customer_name = db.Column(
        db.String(100),
        default="Chat User"
    )

    email = db.Column(
        db.String(100),
        default="Not Provided"
    )

    complaint_text = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        default="General"
    )

    priority = db.Column(
        db.String(20),
        default="Medium"
    )

    sentiment = db.Column(
        db.String(20),
        default="Neutral"
    )

    dispute_risk = db.Column(
        db.String(20),
        default="Unknown"
    )

    status = db.Column(
        db.String(20),
        default="Open"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )