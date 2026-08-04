from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)

from collections import Counter
from models.complaint import (
    Complaint,
    db
)
from models.chat_session import ChatSession
from models.chat_message import ChatMessage

from models.user import User

from services.gemini_service import (
    get_support_reply
)

from services.email_service import (
    send_ticket_email
)

from services.analyzer_service import (
    analyze_complaint
)

from services.ml_services import (
    predict_dispute_risk
)

from models.chat_message import ChatMessage
import uuid


from services.email_service import (
    send_ticket_email,
    send_status_email
)

import plotly.express as px

complaint_bp = Blueprint(
    "complaint",
    __name__
)
import csv
from flask import Response

from sqlalchemy import or_
# ==========================
# Complaint Form
# ==========================
@complaint_bp.route(
    "/complaint",
    methods=["GET", "POST"]
)
def complaint_form():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        #customer_name = request.form[
        #    "customer_name"
        #]

        #email = request.form[
        #    "email"
        #]


        customer_name = session["user_name"]
        email = session["user_email"]

        complaint_text = request.form[
            "complaint_text"
        ]

        analysis = analyze_complaint(
            complaint_text
        )

        risk = predict_dispute_risk(
            complaint_text
        )

        ticket_id = (
            "TKT-" +
            str(uuid.uuid4())[:8].upper()
        )

        complaint = Complaint(
            ticket_id=ticket_id,
            customer_name=customer_name,
            email=email,
            complaint_text=complaint_text,
            category=analysis["category"],
            priority=analysis["priority"],
            sentiment=analysis["sentiment"],
            dispute_risk=risk,
            status="Open"
        )

        db.session.add(
            complaint
        )

        db.session.commit()


        send_ticket_email(
            email,
            customer_name,
            ticket_id
        )

        return (
            f"Complaint submitted! "
            f"Ticket ID: {ticket_id}"
        )

    return render_template(
        "complaint_form.html"
    )


# ==========================
# Track Complaint
# ==========================





@complaint_bp.route(
    "/track",
    methods=["GET", "POST"]
)
def track_complaint():

    complaint = None
    message = None

    if request.method == "POST":

        ticket_id = request.form["ticket_id"]

        complaint = Complaint.query.filter_by(
            ticket_id=ticket_id
        ).first()

        if not complaint:
            message = (
                "❌ Ticket not found."
            )

    return render_template(
        "track_complaint.html",
        complaint=complaint,
        message=message
    )



# ==========================
# Admin Dashboard
# ==========================

@complaint_bp.route("/admin")
def admin_dashboard():

    if ("user_id" not in session or session.get("role") != "admin"):
        return redirect("/login")

    search = request.args.get(
        "search",
        ""
    )

    complaints = Complaint.query

    if search:

        complaints = complaints.filter(
            db.or_(
                Complaint.ticket_id.contains(
                    search
                ),
                Complaint.customer_name.contains(
                    search
                ),
                Complaint.category.contains(
                    search
                ),
                Complaint.status.contains(
                    search
                )
            )
        )

    complaints = complaints.all()

    total = Complaint.query.count()

    open_count = Complaint.query.filter_by(
        status="Open"
    ).count()

    resolved_count = Complaint.query.filter_by(
        status="Resolved"
    ).count()

    high_priority = Complaint.query.filter_by(
        priority="High"
    ).count()

    category_stats = {}
    sentiment_stats = {}

    for complaint in Complaint.query.all():

        category = complaint.category

        if category in category_stats:
            category_stats[category] += 1
        else:
            category_stats[category] = 1

        sentiment = complaint.sentiment

        if sentiment in sentiment_stats:
            sentiment_stats[sentiment] += 1
        else:
            sentiment_stats[sentiment] = 1

    return render_template(
        "admin_dashboard.html",
        complaints=complaints,
        total=total,
        open_count=open_count,
        resolved_count=resolved_count,
        high_priority=high_priority,
        search=search,
        category_stats=category_stats,
        sentiment_stats=sentiment_stats
    )
class Echo:

    def write(self, value):
        return value
    

@complaint_bp.route("/export")
def export_csv():

    complaints = Complaint.query.all()

    def generate():

        data = csv.writer(
            Echo()
        )

        yield data.writerow([
            "Ticket ID",
            "Title",
            "Customer Name",
            "Email",
            "Category",
            "Priority",
            "Sentiment",
            "Status"
        ])

        for complaint in complaints:

            yield data.writerow([
                complaint.ticket_id,
                complaint.title,
                complaint.customer_name,
                complaint.email,
                complaint.category,
                complaint.priority,
                complaint.sentiment,
                complaint.status
            ])

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=complaints.csv"
        }
    )




# ==========================
# Update Ticket Status
# ==========================


@complaint_bp.route(
    "/update/<ticket_id>/<status>"
)
def update_status(
    ticket_id,
    status
):

    complaint = (
        Complaint.query.filter_by(
            ticket_id=ticket_id
        ).first()
    )

    if complaint:

        complaint.status = status

        db.session.commit()

        send_status_email(
            complaint.email,
            complaint.customer_name,
            complaint.ticket_id,
            complaint.status
        )

    return redirect(
        "/admin"
    )


# ==========================
# AI Chatbot
# ==========================
@complaint_bp.route(
    "/chat",
    methods=["GET", "POST"]
)
def chat():

    if "user_id" not in session:
        return redirect("/login")

    # ---------------------------------------------------
    # Create first chat automatically
    # ---------------------------------------------------

    if "chat_session_id" not in session:

        first_chat = ChatSession(

            user_id=session["user_id"],
            title="New Chat"

        )

        db.session.add(first_chat)
        db.session.commit()

        session["chat_session_id"] = first_chat.id

    # ---------------------------------------------------
    # Load all chats of current user
    # ---------------------------------------------------

    chat_sessions = (

        ChatSession.query

        .filter_by(user_id=session["user_id"])

        .order_by(ChatSession.created_at.desc())

        .all()

    )

    # ---------------------------------------------------
    # Load current conversation
    # ---------------------------------------------------

    chat_messages = (

        ChatMessage.query

        .filter_by(
            chat_session_id=session["chat_session_id"]
        )

        .order_by(ChatMessage.id.asc())

        .all()

    )

    messages = [

        {
            "role": m.role,
            "text": m.message
        }

        for m in chat_messages

    ]

    # ---------------------------------------------------
    # POST
    # ---------------------------------------------------

    if request.method == "POST":

        user_message = request.form["message"].strip()

        # Save user message

        db.session.add(

            ChatMessage(

                chat_session_id=session["chat_session_id"],

                role="user",

                message=user_message

            )

        )

        # Auto rename chat

        chat = ChatSession.query.get(

            session["chat_session_id"]

        )

        if chat.title == "New Chat":

            chat.title = user_message[:40]

        db.session.commit()

        # Refresh messages

        messages.append(

            {
                "role": "user",
                "text": user_message
            }

        )

        message_lower = user_message.lower()

        create_ticket = (

            message_lower == "yes"

            and any(

                "create a complaint ticket"

                in msg["text"].lower()

                for msg in messages

                if msg["role"] == "bot"

            )

        )

        # ---------------------------------------------------
        # Ticket creation
        # ---------------------------------------------------

        if create_ticket:

            last_complaint = ""

            for msg in reversed(messages):

                if (

                    msg["role"] == "user"

                    and

                    msg["text"].lower() != "yes"

                ):

                    last_complaint = msg["text"]

                    break

            analysis = analyze_complaint(
                last_complaint
            )

            risk = predict_dispute_risk(
                last_complaint
            )

            ticket_id = (

                "TKT-"

                +

                str(uuid.uuid4())[:8].upper()

            )

            complaint = Complaint(

                ticket_id=ticket_id,

                customer_name=session["user_name"],

                email=session["user_email"],

                complaint_text=last_complaint,

                category=analysis["category"],

                priority=analysis["priority"],

                sentiment=analysis["sentiment"],

                dispute_risk=risk,

                status="Open"

            )

            db.session.add(complaint)

            db.session.commit()

            send_ticket_email(

                session["user_email"],

                session["user_name"],

                ticket_id

            )

            bot_reply = (

                f"🎉 Complaint Registered Successfully\n\n"

                f"🆔 Ticket ID: {ticket_id}\n\n"

                f"📌 Category: {analysis['category']}\n"

                f"⚡ Priority: {analysis['priority']}\n"

                f"😊 Sentiment: {analysis['sentiment']}\n"

                f"🤖 Dispute Risk: {risk}\n\n"

                "Our support team has received your complaint "

                "and will review it as soon as possible.\n\n"

                "Please save your Ticket ID for future tracking."

            )

        else:

            bot_reply = get_support_reply(messages)

        # ---------------------------------------------------
        # Save bot reply
        # ---------------------------------------------------

        db.session.add(

            ChatMessage(

                chat_session_id=session["chat_session_id"],

                role="bot",

                message=bot_reply

            )

        )

        db.session.commit()

        return redirect(url_for("complaint.chat"))

    # ---------------------------------------------------
    # Reload latest messages
    # ---------------------------------------------------

    chat_messages = (

        ChatMessage.query

        .filter_by(

            chat_session_id=session["chat_session_id"]

        )

        .order_by(ChatMessage.id.asc())

        .all()

    )

    messages = [

        {

            "role": m.role,

            "text": m.message

        }

        for m in chat_messages

    ]

    return render_template(

        "chatbot.html",

        messages=messages,

        chat_sessions=chat_sessions

    )
# ==========================
# Clear Chat
# ==========================
@complaint_bp.route(
    "/clear-chat"
)
def clear_chat():

    session.pop(
        "messages",
        None
    )

    return redirect(
        "/chat"
    )


"""@complaint_bp.route(
    "/chat-history"
)
def chat_history():

    chats = (
        ChatMessage.query
        .order_by(
            ChatMessage.created_at
        )
        .all()
    )

    return render_template(
        "chat_history.html",
        chats=chats
    )"""


@complaint_bp.route("/create-ticket")
def create_ticket():

    if "user_id" not in session:
        return redirect("/login")

    messages = session.get(
        "messages",
        []
    )

    last_user_message = ""

    for msg in reversed(messages):

        if msg["role"] == "user":
            last_user_message = msg["text"]
            break

    if not last_user_message:
        return redirect("/chat")

    analysis = analyze_complaint(
        last_user_message
    )
    
    risk = predict_dispute_risk(
        last_user_message
    )

    ticket_id = (
        "TKT-" +
        str(uuid.uuid4())[:8].upper()
    )

    complaint = Complaint(
        ticket_id=ticket_id,
        title=analysis["title"],
        customer_name=session["user_name"],
        email=session["user_email"],
        complaint_text=last_user_message,
        category=analysis["category"],
        priority=analysis["priority"],
        sentiment=analysis["sentiment"],
        dispute_risk=risk,
        status="Open"
    )

    db.session.add(
        complaint
    )

    db.session.commit()

    send_ticket_email(
        session["user_email"],
        session["user_name"],
        ticket_id
    )

    '''bot_reply = (
        f"🎉 Complaint Registered Successfully\n\n"
        f"🆔 Ticket ID: {ticket_id}\n\n"
        f"Thank you for contacting us.\n"
        f"Our support team will review your complaint shortly.\n\n"
        f"You can track your complaint using this Ticket ID."
    )'''

    bot_reply = (
        f"🎉 Complaint Registered Successfully\n\n"
        f"🆔 Ticket ID: {ticket_id}\n\n"
        f"📌 Category: {analysis['category']}\n"
        f"⚡ Priority: {analysis['priority']}\n"
        f"😊 Sentiment: {analysis['sentiment']}\n"
        f"🤖 Dispute Risk: {risk}\n\n"
        f"Our support team has received your complaint "
        f"and will review it shortly.\n\n"
        f"Please save your Ticket ID for future tracking."
    )

    messages.append(
        {
            "role": "bot",
            "text": bot_reply
        }
    )

    session["messages"] = messages

    return redirect("/chat")



@complaint_bp.route(
    "/complaint/<ticket_id>"
)
def complaint_details(ticket_id):

    complaint = Complaint.query.filter_by(
        ticket_id=ticket_id
    ).first_or_404()

    return render_template(
        "complaint_details.html",
        complaint=complaint
    )


@complaint_bp.route(
    "/user_register",
    methods=["GET", "POST"]
)
def user_register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(
            email=email
        ).first()
        


        if existing_user:


            flash(
                "Email already registered. Please login.",
                "danger"
            )
            
            return redirect(
                "/register"
            )

        user = User(
            name=name,
            email=email,
            password=password,
            role="customer"
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template(
        "register.html"
    )

@complaint_bp.route(
    "/admin_register",
    methods=["GET", "POST"]
)
def admin_register():

    if request.method == "POST":

        name = request.form["name"]

        email = request.form["email"]

        password = request.form["password"]

        secret_key = request.form[
            "secret_key"
        ]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                "/admin_register"
            )

        if (
            secret_key
            !=
            "COMPLAINT_AI_2026"
        ):

            flash(
                "Invalid Admin Secret Key.",
                "danger"
            )

            return redirect(
                "/admin_register"
            )

        user = User(
            name=name,
            email=email,
            password=password,
            role="admin"
        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Admin account created successfully!",
            "success"
        )

        return redirect(
            "/admin_login"
        )

    return render_template(
        "admin_register.html"
    )

@complaint_bp.route(
    "/user_login",
    methods=["GET", "POST"]
)
def user_login():

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip()

        password = request.form[
            "password"
        ].strip()

        user = User.query.filter_by(
            email=email,
            role="customer"
        ).first()

        if (
            user
            and
            user.password == password
        ):

            session["user_id"] = (
                user.id
            )

            session["user_name"] = (
                user.name
            )

            session["user_email"] = (
                user.email
            )

            session["role"] = (
                user.role
            )

            return redirect(
                "/dashboard"
            )

        flash(
            "Invalid Customer Credentials",
            "danger"
        )

    return render_template(
        "login.html"
    )


@complaint_bp.route(
    "/admin_login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        email = request.form[
            "email"
        ].strip()

        password = request.form[
            "password"
        ].strip()

        user = User.query.filter_by(
            email=email,
            role="admin"
        ).first()

        if (
            user
            and
            user.password == password
        ):

            session["user_id"] = (
                user.id
            )

            session["user_name"] = (
                user.name
            )

            session["user_email"] = (
                user.email
            )

            session["role"] = (
                user.role
            )

            return redirect(
                "/admin"
            )

        flash(
            "Invalid Administrator Credentials",
            "danger"
        )

    return render_template(
        "admin_login.html"
    )

@complaint_bp.route(
    "/logout"
)
def logout():

    session.clear()

    return redirect(
        "/"
    )


@complaint_bp.route(
    "/my-complaints"
)
def my_complaints():


    if "user_id" not in session:
        return redirect("/login")

    email = session[
        "user_email"
    ]

    complaints = Complaint.query.filter_by(
        email=email
    ).all()

    return render_template(
        "my_complaints.html",
        complaints=complaints
    )


@complaint_bp.route("/test-mail")
def test_mail():

    success = send_ticket_email(
        "valluriumesh@gmail.com",   # put your email here
        "Umesh",
        "TEST-123"
    )

    if success:
        return "Mail function executed."

    return "Mail failed."


@complaint_bp.route(
    "/ticket/<ticket_id>"
)
def ticket_details(
    ticket_id
):

    complaint = (
        Complaint.query.filter_by(
            ticket_id=ticket_id
        ).first_or_404()
    )

    return render_template(
        "ticket_details.html",
        complaint=complaint
    )

@complaint_bp.route(
    "/voice"
)
def voice():
    return render_template(
        "voice.html"
    )

@complaint_bp.route("/")
def home():

    return render_template(
        "index.html"
    )

@complaint_bp.route("/login")
def login_choice():

    return render_template(
        "login_choice.html"
    )


@complaint_bp.route("/register")
def register_choice():

    return render_template(
        "register_choice.html"
    )


@complaint_bp.route("/dashboard")
def dashboard():

    if not session.get("user_id"):

        return redirect(
            "/login"
        )

    user_email = session.get(
        "user_email"
    )

    total_complaints = Complaint.query.filter_by(
        email=user_email
    ).count()

    open_complaints = Complaint.query.filter_by(
        email=user_email,
        status="Open"
    ).count()

    resolved_complaints = Complaint.query.filter_by(
        email=user_email,
        status="Resolved"
    ).count()

    high_priority = Complaint.query.filter_by(
        email=user_email,
        priority="High"
    ).count()

    return render_template(

        "dashboard.html",

        total_complaints=total_complaints,

        open_complaints=open_complaints,

        resolved_complaints=resolved_complaints,

        high_priority=high_priority

    )


@complaint_bp.route("/admin/complaints")
def admin_complaints():
    return render_template("admin_complaints.html")



@complaint_bp.route("/admin/customers")
def admin_customers():

    if session.get("role") != "admin":
        return redirect("/admin/login")

    #users = User.query.order_by(User.id.desc()).all()
    users = User.query.filter_by(role="customer").all()

    return render_template(
        "admin_customers.html",
        users=users
    )


@complaint_bp.route("/new-chat")
def new_chat():

    if "user_id" not in session:
        return redirect("/login")

    new_chat = ChatSession(

        user_id=session["user_id"],

        title="New Chat"

    )

    db.session.add(new_chat)

    db.session.commit()

    session["chat_session_id"] = new_chat.id

    return redirect(url_for("complaint.chat"))


@complaint_bp.route("/chat/<int:chat_id>")
def open_chat(chat_id):

    if "user_id" not in session:
        return redirect("/login")

    chat = ChatSession.query.filter_by(

        id=chat_id,
        user_id=session["user_id"]

    ).first_or_404()

    session["chat_session_id"] = chat.id

    return redirect(url_for("complaint.chat"))

@complaint_bp.route("/admin/analytics")
def admin_analytics():

    if session.get("role") != "admin":
        return redirect("/admin/login")

    complaints = Complaint.query.all()

    total = len(complaints)

    open_count = Complaint.query.filter_by(
        status="Open"
    ).count()

    resolved_count = Complaint.query.filter_by(
        status="Resolved"
    ).count()

    high_priority = Complaint.query.filter_by(
        priority="High"
    ).count()

    categories = {}

    priorities = {}

    sentiments = {}

    risks = {}

    for complaint in complaints:

        categories[
            complaint.category or "Unknown"
        ] = categories.get(
            complaint.category or "Unknown",
            0
        ) + 1

        priorities[
            complaint.priority or "Unknown"
        ] = priorities.get(
            complaint.priority or "Unknown",
            0
        ) + 1

        sentiments[
            complaint.sentiment or "Unknown"
        ] = sentiments.get(
            complaint.sentiment or "Unknown",
            0
        ) + 1

        risks[
            complaint.dispute_risk or "Unknown"
        ] = risks.get(
            complaint.dispute_risk or "Unknown",
            0
        ) + 1

    return render_template(

        "admin_analytics.html",

        total=total,

        open_count=open_count,

        resolved_count=resolved_count,

        high_priority=high_priority,

        categories=categories,

        priorities=priorities,

        sentiments=sentiments,

        risks=risks,

        complaints=complaints[-10:]

    )