from flask_mail import Message
from extensions import mail


def send_ticket_email(
    email,
    customer_name,
    ticket_id
):

    try:

        print(
            f"Sending email to: {email}"
        )

        msg = Message(
            subject="Complaint Registered Successfully",
            sender="myspamm2000@gmail.com",
            recipients=[email]
        )

        msg.body = f"""
Hello {customer_name},

Your complaint has been registered successfully.

Ticket ID:
{ticket_id}

Status:
Open

Please save this Ticket ID for future tracking.

Thank you,
Complaint AI Team
"""

        mail.send(msg)

        print(
            "Email sent successfully!"
        )

        return True

    except Exception as e:

        print(
            f"Email Error: {e}"
        )

        return False
    

def send_status_email(
    email,
    customer_name,
    ticket_id,
    status
):

    try:

        msg = Message(
            subject="Complaint Status Updated",
            sender="myspamm2000@gmail.com",
            recipients=[email]
        )

        msg.body = f"""
Hello {customer_name},

Your complaint status has been updated.

Ticket ID:
{ticket_id}

New Status:
{status}

Thank you,
Complaint AI Team
"""

        mail.send(msg)

        return True

    except Exception as e:

        print(
            f"Status Email Error: {e}"
        )

        return False
    

