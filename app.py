from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

from functools import wraps
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import get_db, init_db, DEPARTMENTS
from allocation import recommend_allocations

from datetime import datetime, date


app = Flask(__name__)
app.secret_key = "lablink_secret_key"

init_db()


YEARS = [
    "1st Year",
    "2nd Year",
    "3rd Year",
    "4th Year"
]

SEMESTERS = [
    "1st Semester",
    "2nd Semester",
    "3rd Semester",
    "4th Semester",
    "5th Semester",
    "6th Semester",
    "7th Semester",
    "8th Semester"
]


# =====================================================
# DEPARTMENT COMPATIBILITY
# =====================================================

DEPARTMENT_ALIASES = {
    "Computer Science and Engineering": [
        "Computer Science and Engineering",
        "Computer Science"
    ],

    "Electronics and Communication Engineering": [
        "Electronics and Communication Engineering",
        "Electronics"
    ],

    "Mechanical Engineering": [
        "Mechanical Engineering",
        "Mechanical"
    ]
}


def canonical_department(department):

    department = (department or "").strip()

    for canonical, aliases in DEPARTMENT_ALIASES.items():

        if department in aliases:
            return canonical

    return department


def get_department_names(department):

    canonical = canonical_department(department)

    return DEPARTMENT_ALIASES.get(
        canonical,
        [canonical]
    )


def department_placeholders(department):

    names = get_department_names(department)

    placeholders = ",".join(["?"] * len(names))

    return names, placeholders


# =====================================================
# LOGIN PROTECTION
# =====================================================

def login_required(role=None):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            if "user_id" not in session:

                flash("Please login first.", "warning")

                return redirect(url_for("index"))

            if role and session.get("role") != role:

                flash("Unauthorised access.", "danger")

                return redirect(url_for("index"))

            return function(*args, **kwargs)

        return wrapper

    return decorator


# =====================================================
# HOME
# =====================================================

@app.route("/")
def index():

    return render_template("index.html")


# =====================================================
# STUDENT AND FACULTY ACCESS
# =====================================================

@app.route("/student-access")
def student_access():

    return render_template(
        "auth_choice.html",
        role="student",
        role_title="Student"
    )


@app.route("/faculty-access")
def faculty_access():

    return render_template(
        "auth_choice.html",
        role="faculty",
        role_title="Faculty"
    )


# =====================================================
# REGISTRATION
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    role = request.args.get(
        "role",
        request.form.get("role", "student")
    ).lower()

    if role not in ["student", "faculty"]:
        role = "student"

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        department = request.form.get(
            "department", ""
        ).strip()

        usn = request.form.get("usn", "").strip()

        academic_year = request.form.get(
            "academic_year", ""
        )

        semester = request.form.get(
            "semester", ""
        )

        faculty_id = request.form.get(
            "faculty_id", ""
        ).strip()

        designation = request.form.get(
            "designation", ""
        ).strip()

        if not all([name, email, password, department]):

            flash(
                "Please fill all required fields.",
                "danger"
            )

        elif len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

        elif role == "student" and not all([
            usn,
            academic_year,
            semester
        ]):

            flash(
                "Enter USN, academic year and semester.",
                "danger"
            )

        elif role == "faculty" and not faculty_id:

            flash(
                "Enter your Faculty ID.",
                "danger"
            )

        elif department not in DEPARTMENTS:

            flash(
                "Select a valid department.",
                "danger"
            )

        else:

            conn = get_db()

            try:

                conn.execute("""
                    INSERT INTO users (
                        name,
                        email,
                        password,
                        role,
                        department,
                        usn,
                        academic_year,
                        semester,
                        faculty_id,
                        designation
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    email,
                    generate_password_hash(password),
                    role,
                    department,
                    usn if role == "student" else None,
                    academic_year if role == "student" else None,
                    semester if role == "student" else None,
                    faculty_id if role == "faculty" else None,
                    designation if role == "faculty" else None
                ))

                conn.commit()

                flash(
                    "Registration successful! Please login.",
                    "success"
                )

                return redirect(
                    url_for("login", role=role)
                )

            except Exception as error:

                print("REGISTRATION ERROR:", error)

                flash(
                    "Email or ID may already be registered.",
                    "danger"
                )

            finally:
                conn.close()

    return render_template(
        "register.html",
        role=role,
        departments=DEPARTMENTS,
        years=YEARS,
        semesters=SEMESTERS
    )


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    role = request.args.get(
        "role",
        request.form.get("role", "student")
    ).lower()

    if role not in ["student", "faculty"]:
        role = "student"

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        conn = get_db()

        try:

            user = conn.execute("""
                SELECT *
                FROM users
                WHERE email = ?
                AND role = ?
            """, (email, role)).fetchone()

        finally:
            conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session.clear()

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            session["department"] = canonical_department(
                user["department"]
            )

            if role == "student":

                return redirect(
                    url_for("student_dashboard")
                )

            return redirect(
                url_for("faculty_dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html",
        role=role
    )


# =====================================================
# FORGOT PASSWORD
# =====================================================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    role = request.args.get(
        "role",
        request.form.get("role", "student")
    ).lower()

    if role not in ["student", "faculty"]:
        role = "student"

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        new_password = request.form.get(
            "new_password", ""
        )

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        conn = get_db()

        try:

            user = conn.execute("""
                SELECT *
                FROM users
                WHERE email = ?
                AND role = ?
            """, (email, role)).fetchone()

            if not user:

                flash(
                    "Account not found.",
                    "danger"
                )

            elif len(new_password) < 6:

                flash(
                    "Password must contain at least 6 characters.",
                    "danger"
                )

            elif new_password != confirm_password:

                flash(
                    "Passwords do not match.",
                    "danger"
                )

            else:

                conn.execute("""
                    UPDATE users
                    SET password = ?
                    WHERE id = ?
                """, (
                    generate_password_hash(new_password),
                    user["id"]
                ))

                conn.commit()

                flash(
                    "Password updated successfully!",
                    "success"
                )

                return redirect(
                    url_for("login", role=role)
                )

        finally:
            conn.close()

    return render_template(
        "forgot_password.html",
        role=role
    )


# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have logged out successfully.",
        "success"
    )

    return redirect(url_for("index"))


# =====================================================
# STUDENT DASHBOARD
# =====================================================

@app.route("/student")
@login_required("student")
def student_dashboard():

    conn = get_db()

    try:

        user = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
        """, (session["user_id"],)).fetchone()

        bookings = conn.execute("""
            SELECT
                b.*,
                e.name AS equipment_name,
                e.department AS equipment_department

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE b.student_id = ?

            ORDER BY b.id DESC
        """, (session["user_id"],)).fetchall()

        total = len(bookings)

        pending = sum(
            1 for b in bookings
            if b["status"] == "Pending"
        )

        approved = sum(
            1 for b in bookings
            if b["status"] == "Approved"
        )

    finally:
        conn.close()

    return render_template(
        "student_dashboard.html",
        user=user,
        bookings=bookings,
        total=total,
        pending=pending,
        approved=approved
    )


# =====================================================
# FACULTY DASHBOARD
# =====================================================

@app.route("/faculty")
@login_required("faculty")
def faculty_dashboard():

    conn = get_db()

    try:

        faculty = conn.execute("""
            SELECT *
            FROM users
            WHERE id = ?
            AND role = 'faculty'
        """, (session["user_id"],)).fetchone()

        if not faculty:

            session.clear()

            flash(
                "Faculty account not found.",
                "danger"
            )

            return redirect(url_for("index"))

        names, placeholders = department_placeholders(
            faculty["department"]
        )

        # Faculty receives requests for equipment
        # belonging to their department.
        #
        # Student department is NOT restricted.

        pending_requests = conn.execute(f"""
            SELECT
                b.*,

                u.name AS student_name,
                u.email AS student_email,
                u.department AS student_department,
                u.academic_year,
                u.semester,
                u.usn,

                e.name AS equipment_name,
                e.department AS equipment_department,
                e.quantity AS equipment_quantity

            FROM bookings b

            JOIN users u
            ON b.student_id = u.id

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE b.status = 'Pending'

            AND e.department IN ({placeholders})

            ORDER BY b.deadline ASC, b.id DESC
        """, names).fetchall()

        approved_count = conn.execute(f"""
            SELECT COUNT(*)

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE e.department IN ({placeholders})

            AND b.status = 'Approved'
        """, names).fetchone()[0]

        total_requests = len(pending_requests)

    finally:
        conn.close()

    return render_template(
        "faculty_dashboard.html",
        faculty=faculty,
        requests=pending_requests,
        pending=pending_requests,
        total_requests=total_requests,
        pending_count=total_requests,
        approved_count=approved_count
    )


# =====================================================
# EQUIPMENT DISCOVERY
# =====================================================

@app.route("/equipment")
@login_required("student")
def equipment():

    department = request.args.get(
        "department", ""
    ).strip()

    if department and department not in DEPARTMENTS:
        department = ""

    conn = get_db()

    try:

        today = date.today().strftime("%Y-%m-%d")

        current_time = datetime.now().strftime("%H:%M")

        query = """
            SELECT
                e.*,

                (
                    SELECT COUNT(*)

                    FROM bookings b

                    WHERE b.equipment_id = e.id

                    AND b.booking_date = ?

                    AND b.start_time <= ?

                    AND b.end_time > ?

                    AND b.status IN ('Pending', 'Approved')

                ) AS booked_now,

                (
                    SELECT COUNT(*)

                    FROM bookings b

                    WHERE b.equipment_id = e.id

                    AND b.status = 'Pending'

                ) AS pending_count,

                (
                    SELECT COUNT(*)

                    FROM bookings b

                    WHERE b.equipment_id = e.id

                    AND b.status = 'Approved'

                ) AS approved_count,

                (
                    SELECT COUNT(*)

                    FROM bookings b

                    WHERE b.equipment_id = e.id

                    AND b.status IN ('Pending', 'Approved')

                ) AS total_bookings

            FROM equipment e

            WHERE 1=1
        """

        params = [
            today,
            current_time,
            current_time
        ]

        if department:

            aliases = get_department_names(department)

            placeholders = ",".join(
                ["?"] * len(aliases)
            )

            query += f"""
                AND e.department IN ({placeholders})
            """

            params.extend(aliases)

        query += """
            ORDER BY e.department, e.name
        """

        records = conn.execute(
            query,
            params
        ).fetchall()

        items = []

        for item in records:

            data = dict(item)

            data["available_now"] = max(
                0,
                item["quantity"] - item["booked_now"]
            )

            items.append(data)

    finally:
        conn.close()

    return render_template(
        "equipment.html",
        items=items,
        departments=DEPARTMENTS,
        selected_department=department
    )


# =====================================================
# CHECK BOOKING SLOT
# =====================================================

def get_booked_count(
    conn,
    equipment_id,
    booking_date,
    start_time,
    end_time,
    exclude_booking_id=None
):

    query = """
        SELECT COUNT(*)

        FROM bookings

        WHERE equipment_id = ?

        AND booking_date = ?

        AND status IN ('Pending', 'Approved')

        AND start_time < ?

        AND end_time > ?
    """

    params = [
        equipment_id,
        booking_date,
        end_time,
        start_time
    ]

    if exclude_booking_id is not None:

        query += """
            AND id != ?
        """

        params.append(exclude_booking_id)

    return conn.execute(
        query,
        params
    ).fetchone()[0]


# =====================================================
# FIND ALTERNATIVE SLOTS
# =====================================================

def find_alternative_slots(
    conn,
    equipment_id,
    booking_date,
    duration_minutes,
    quantity
):

    alternatives = []

    start_minutes = 9 * 60

    closing_minutes = 18 * 60

    while start_minutes + duration_minutes <= closing_minutes:

        end_minutes = start_minutes + duration_minutes

        start = (
            f"{start_minutes // 60:02d}:"
            f"{start_minutes % 60:02d}"
        )

        end = (
            f"{end_minutes // 60:02d}:"
            f"{end_minutes % 60:02d}"
        )

        count = get_booked_count(
            conn,
            equipment_id,
            booking_date,
            start,
            end
        )

        if count < quantity:

            alternatives.append({
                "date": booking_date,
                "start": start,
                "end": end
            })

        if len(alternatives) >= 3:
            break

        start_minutes += 30

    return alternatives


# =====================================================
# BOOK EQUIPMENT
# =====================================================

@app.route(
    "/book/<int:equipment_id>",
    methods=["GET", "POST"]
)
@login_required("student")
def book_equipment(equipment_id):

    conn = get_db()

    try:

        item = conn.execute("""
            SELECT *
            FROM equipment
            WHERE id = ?
        """, (equipment_id,)).fetchone()

        if not item:

            flash(
                "Equipment not found.",
                "danger"
            )

            return redirect(url_for("equipment"))

        if request.method == "POST":

            project_name = request.form.get(
                "project_name", ""
            ).strip()

            purpose = request.form.get(
                "purpose", ""
            ).strip()

            requirements = (
                request.form.get("technical_requirements", "")
                or request.form.get("requirements", "")
            ).strip()

            booking_date = request.form.get(
                "booking_date", ""
            )

            start_time = request.form.get(
                "start_time", ""
            )

            end_time = request.form.get(
                "end_time", ""
            )

            deadline = (
                request.form.get("project_deadline", "")
                or request.form.get("deadline", "")
            )

            if not all([
                project_name,
                purpose,
                booking_date,
                start_time,
                end_time,
                deadline
            ]):

                flash(
                    "Please complete all required fields.",
                    "danger"
                )

                return redirect(url_for(
                    "book_equipment",
                    equipment_id=equipment_id
                ))

            try:

                booking_day = datetime.strptime(
                    booking_date,
                    "%Y-%m-%d"
                ).date()

                deadline_day = datetime.strptime(
                    deadline,
                    "%Y-%m-%d"
                ).date()

                start = datetime.strptime(
                    start_time,
                    "%H:%M"
                )

                end = datetime.strptime(
                    end_time,
                    "%H:%M"
                )

                if booking_day < date.today():
                    raise ValueError

                if deadline_day < booking_day:
                    raise ValueError

                if end <= start:
                    raise ValueError

                if start.minute not in [0, 30]:
                    raise ValueError

                if end.minute not in [0, 30]:
                    raise ValueError

                if start.hour < 9 or end.hour > 18:
                    raise ValueError

                if booking_day == date.today():

                    if start.time() <= datetime.now().time():
                        raise ValueError

            except ValueError:

                flash(
                    "Invalid date or time. Choose a future slot between 09:00 and 18:00.",
                    "danger"
                )

                return redirect(url_for(
                    "book_equipment",
                    equipment_id=equipment_id
                ))

            # Check overlapping bookings.

            count = get_booked_count(
                conn,
                equipment_id,
                booking_date,
                start_time,
                end_time
            )

            if count >= item["quantity"]:

                duration_minutes = int(
                    (end - start).total_seconds() / 60
                )

                alternatives = find_alternative_slots(
                    conn,
                    equipment_id,
                    booking_date,
                    duration_minutes,
                    item["quantity"]
                )

                return render_template(
                    "booking.html",
                    item=item,
                    alternatives=alternatives,
                    conflict=True
                )

            # Save request.

            conn.execute("""
                INSERT INTO bookings (
                    student_id,
                    equipment_id,
                    project_name,
                    purpose,
                    requirements,
                    booking_date,
                    start_time,
                    end_time,
                    deadline,
                    status
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
            """, (
                session["user_id"],
                equipment_id,
                project_name,
                purpose,
                requirements,
                booking_date,
                start_time,
                end_time,
                deadline
            ))

            conn.commit()

            flash(
                "Booking request submitted successfully! Waiting for faculty approval.",
                "success"
            )

            return redirect(
                url_for("student_dashboard")
            )

        return render_template(
            "booking.html",
            item=item,
            alternatives=[],
            conflict=False
        )

    except Exception as error:

        conn.rollback()

        print("BOOKING ERROR:", error)

        flash(
            "Unable to process booking. Please try again.",
            "danger"
        )

        return redirect(url_for("equipment"))

    finally:
        conn.close()


# =====================================================
# APPROVE BOOKING
# =====================================================

@app.route(
    "/approve/<int:booking_id>",
    methods=["POST"]
)
@login_required("faculty")
def approve(booking_id):

    conn = get_db()

    try:

        booking = conn.execute("""
            SELECT
                b.*,
                e.quantity,
                e.department

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE b.id = ?
        """, (booking_id,)).fetchone()

        if not booking:

            flash(
                "Booking request not found.",
                "danger"
            )

            return redirect(url_for("faculty_dashboard"))

        allowed_departments = get_department_names(
            session["department"]
        )

        if booking["department"] not in allowed_departments:

            flash(
                "You are not authorised to approve this request.",
                "danger"
            )

            return redirect(url_for("faculty_dashboard"))

        if booking["status"] != "Pending":

            flash(
                "This request has already been processed.",
                "warning"
            )

            return redirect(url_for("faculty_dashboard"))

        count = get_booked_count(
            conn,
            booking["equipment_id"],
            booking["booking_date"],
            booking["start_time"],
            booking["end_time"],
            exclude_booking_id=booking_id
        )

        if count >= booking["quantity"]:

            flash(
                "This time slot is no longer available.",
                "danger"
            )

            return redirect(url_for("faculty_dashboard"))

        conn.execute("""
            UPDATE bookings

            SET status = 'Approved'

            WHERE id = ?

            AND status = 'Pending'
        """, (booking_id,))

        conn.commit()

        flash(
            "Booking approved successfully!",
            "success"
        )

    except Exception as error:

        conn.rollback()

        print("APPROVAL ERROR:", error)

        flash(
            "Unable to approve this booking.",
            "danger"
        )

    finally:
        conn.close()

    return redirect(url_for("faculty_dashboard"))


# =====================================================
# REJECT BOOKING
# =====================================================

@app.route(
    "/reject/<int:booking_id>",
    methods=["POST"]
)
@login_required("faculty")
def reject(booking_id):

    conn = get_db()

    try:

        booking = conn.execute("""
            SELECT
                b.id,
                b.status,
                e.department

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE b.id = ?
        """, (booking_id,)).fetchone()

        if not booking:

            flash(
                "Booking request not found.",
                "danger"
            )

            return redirect(url_for("faculty_dashboard"))

        allowed_departments = get_department_names(
            session["department"]
        )

        if booking["department"] not in allowed_departments:

            flash(
                "You are not authorised to reject this request.",
                "danger"
            )

            return redirect(url_for("faculty_dashboard"))

        if booking["status"] != "Pending":

            flash(
                "This request has already been processed.",
                "warning"
            )

            return redirect(url_for("faculty_dashboard"))

        note = request.form.get(
            "faculty_note", ""
        ).strip()

        conn.execute("""
            UPDATE bookings

            SET status = 'Rejected',
                faculty_note = ?

            WHERE id = ?

            AND status = 'Pending'
        """, (note, booking_id))

        conn.commit()

        flash(
            "Booking rejected.",
            "info"
        )

    except Exception as error:

        conn.rollback()

        print("REJECTION ERROR:", error)

        flash(
            "Unable to reject this booking.",
            "danger"
        )

    finally:
        conn.close()

    return redirect(url_for("faculty_dashboard"))


# =====================================================
# BOOKING HISTORY
# =====================================================

@app.route("/bookings")
@login_required()
def bookings():

    conn = get_db()

    try:

        if session["role"] == "student":

            records = conn.execute("""
                SELECT
                    b.*,
                    u.name AS student_name,
                    e.name AS equipment_name,
                    e.department AS equipment_department

                FROM bookings b

                JOIN users u
                ON b.student_id = u.id

                JOIN equipment e
                ON b.equipment_id = e.id

                WHERE b.student_id = ?

                ORDER BY b.id DESC
            """, (session["user_id"],)).fetchall()

        else:

            names, placeholders = department_placeholders(
                session["department"]
            )

            records = conn.execute(f"""
                SELECT
                    b.*,
                    u.name AS student_name,
                    u.department AS student_department,
                    u.academic_year,
                    u.semester,
                    e.name AS equipment_name,
                    e.department AS equipment_department

                FROM bookings b

                JOIN users u
                ON b.student_id = u.id

                JOIN equipment e
                ON b.equipment_id = e.id

                WHERE e.department IN ({placeholders})

                ORDER BY b.id DESC
            """, names).fetchall()

    finally:
        conn.close()

    return render_template(
        "requests.html",
        bookings=records
    )


# =====================================================
# AI ALLOCATION
# =====================================================

@app.route("/allocation")
@login_required("faculty")
def allocation():

    conn = get_db()

    try:

        names, placeholders = department_placeholders(
            session["department"]
        )

        pending = conn.execute(f"""
            SELECT
                b.*,
                u.name AS student_name,
                u.department AS student_department,
                u.academic_year,
                u.semester,
                e.name AS equipment_name,
                e.quantity AS equipment_quantity

            FROM bookings b

            JOIN users u
            ON b.student_id = u.id

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE b.status = 'Pending'

            AND e.department IN ({placeholders})

            ORDER BY b.deadline ASC
        """, names).fetchall()

        recommendations = recommend_allocations(pending)

    finally:
        conn.close()

    return render_template(
        "analytics.html",
        recommendations=recommendations,
        mode="allocation"
    )


# =====================================================
# ANALYTICS
# =====================================================

@app.route("/analytics")
@login_required("faculty")
def analytics():

    conn = get_db()

    try:

        names, placeholders = department_placeholders(
            session["department"]
        )

        total_bookings = conn.execute(f"""
            SELECT COUNT(*)

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE e.department IN ({placeholders})
        """, names).fetchone()[0]

        approved = conn.execute(f"""
            SELECT COUNT(*)

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE e.department IN ({placeholders})

            AND b.status = 'Approved'
        """, names).fetchone()[0]

        pending = conn.execute(f"""
            SELECT COUNT(*)

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE e.department IN ({placeholders})

            AND b.status = 'Pending'
        """, names).fetchone()[0]

        rejected = conn.execute(f"""
            SELECT COUNT(*)

            FROM bookings b

            JOIN equipment e
            ON b.equipment_id = e.id

            WHERE e.department IN ({placeholders})

            AND b.status = 'Rejected'
        """, names).fetchone()[0]

        equipment_usage = conn.execute(f"""
            SELECT
                e.name,
                COUNT(b.id) AS total

            FROM equipment e

            LEFT JOIN bookings b
            ON e.id = b.equipment_id

            WHERE e.department IN ({placeholders})

            GROUP BY e.id

            ORDER BY total DESC
        """, names).fetchall()

    finally:
        conn.close()

    return render_template(
        "analytics.html",
        total_bookings=total_bookings,
        approved=approved,
        pending=pending,
        rejected=rejected,
        equipment_usage=equipment_usage,
        mode="analytics"
    )


# =====================================================
# START APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)