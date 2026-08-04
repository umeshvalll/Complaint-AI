from flask import Flask, render_template
from flask_session import Session

from config import Config
from extensions import mail

from models.user import User
from models.complaint import db
from models.chat_message import ChatMessage

from models.chat_session import ChatSession

from routes.complaint_routes import (
    complaint_bp
)

from routes.admin_routes import (
    admin_bp
)

app = Flask(__name__)

app.config.from_object(
    Config
)

app.config["SECRET_KEY"] = Config.SECRET_KEY

app.config["MAIL_SERVER"] = Config.MAIL_SERVER
app.config["MAIL_PORT"] = Config.MAIL_PORT
app.config["MAIL_USE_TLS"] = Config.MAIL_USE_TLS
app.config["MAIL_USERNAME"] = Config.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = Config.MAIL_PASSWORD
app.config["MAIL_DEFAULT_SENDER"] = Config.MAIL_USERNAME

Session(app)

mail.init_app(app)

db.init_app(app)

app.register_blueprint(
    complaint_bp
)

app.register_blueprint(
    admin_bp
)

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        email="admin@complaintai.com"
    ).first()

    if not admin:

        admin = User(

            name="Admin",

            email=
            "admin@complaintai.com",

            password=
            "Admin@123",

            role=
            "admin"

        )

        db.session.add(
            admin
        )

        db.session.commit()


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )