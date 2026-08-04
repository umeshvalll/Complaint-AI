from models.complaint import db


class User(db.Model):

    __tablename__ = "user"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(100)
    )

    role = db.Column(
        db.String(20),
        default="customer"
    )

    chat_sessions = db.relationship(
        "ChatSession",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )