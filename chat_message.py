from models.complaint import db
from datetime import datetime


class ChatMessage(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    chat_session_id = db.Column(
        db.Integer,
        db.ForeignKey("chat_session.id"),
        nullable=False
    )

    role = db.Column(
        db.String(20)
    )

    message = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )