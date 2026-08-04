from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models.user import User
from models.complaint import db

admin_bp = Blueprint(
    "admin",
    __name__
)

ADMIN_SECRET = (
    "COMPLAINT_AI_2026"
)

@admin_bp.route(
    "/admin-register",
    methods=["GET", "POST"]
)
def admin_register():

    if request.method == "POST":

        if (
            request.form[
                "secret_key"
            ]
            != ADMIN_SECRET
        ):

            flash(
                "Invalid Admin Secret Key!",
                "danger"
            )

            return redirect(
                "/admin-register"
            )

        user = User(

            name=request.form[
                "name"
            ],

            email=request.form[
                "email"
            ],

            password=
            generate_password_hash(
                request.form[
                    "password"
                ]
            ),

            role="admin"

        )

        db.session.add(
            user
        )

        db.session.commit()

        flash(
            "Admin Created!",
            "success"
        )

        return redirect(
            "/admin-login"
        )

    return render_template(
        "admin_register.html"
    )

@admin_bp.route(
    "/admin-login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        user = User.query.filter_by(

            email=request.form[
                "email"
            ],

            role="admin"

        ).first()

        if (
            user
            and
            check_password_hash(
                user.password,
                request.form[
                    "password"
                ]
            )
        ):

            session[
                "user_id"
            ] = user.id

            session[
                "role"
            ] = "admin"

            session[
                "user_name"
            ] = user.name

            return redirect(
                "/admin"
            )

        flash(
            "Invalid Credentials",
            "danger"
        )

    return render_template(
        "admin_login.html"
    )