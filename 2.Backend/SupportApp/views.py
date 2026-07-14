from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pymysql


def get_db_connection():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        database='webdb13',
        cursorclass=pymysql.cursors.DictCursor
    )


def ensure_single_admin():
    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()
            cur.execute("SELECT id FROM users1 WHERE role='admin'")
            admin = cur.fetchone()

            if not admin:
                cur.execute("""
                    INSERT INTO users1
                    (username, email, password, mobile, address, role, approved)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (
                    "admin",
                    "admin@gmail.com",
                    "admin",
                    "1234567890",
                    "Hyderabad",
                    "admin",
                    1
                ))
                con.commit()

    except Exception as e:
        print("Admin Error:", e)



@api_view(["POST"])
def register_api(request):
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    confirm = request.data.get("confirm_password")
    mobile = request.data.get("mobile")
    address = request.data.get("address")
    role ="user"

    if password != confirm:
        return Response({"error": "Passwords do not match"})

    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()

            
            cur.execute("SELECT username FROM users1 WHERE username=%s", (username,))
            if cur.fetchone():
                return Response({"error": "Username already exists"})

            cur.execute("SELECT email FROM users1 WHERE email=%s", (email,))
            if cur.fetchone():
                return Response({"error": "Email already exists"})

            cur.execute("SELECT mobile FROM users1 WHERE mobile=%s", (mobile,))
            if cur.fetchone():
                return Response({"error": "Mobile already exists"})

            
            cur.execute("""
                INSERT INTO users1
                (username, email, password, role, approved, mobile, address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, email, password, role, 0, mobile, address))

            con.commit()
            return Response({"success": "Account created. Awaiting Admin approval"})

    except Exception as e:
        return Response({"error": "Database error: " + str(e)})




@api_view(["POST"])
def login_api(request):
    ensure_single_admin()

    username = request.data.get("username")
    password = request.data.get("password")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM users1 WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()

    if not user:
        return Response({"error": "Invalid login credentials"})

    if user["approved"] == 0:
        return Response({"error": "Account not approved yet"})

    return Response({
        "success": "Login successful",
        "username": user["username"],
        "role": user["role"]
    })



@api_view(["GET"])
def admin_user_api(request):
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users1 WHERE role='user'")
        users = cur.fetchall()

    return Response({"users": users}) 



@api_view(["POST"])
def approve_user_api(request):
    username = request.data.get("username")

    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()
            cur.execute("UPDATE users1 SET approved=1 WHERE username=%s", (username,))
            con.commit()

        return Response({"success": "user approved successfully"})

    except Exception as e:
        return Response({"error": str(e)})


@api_view(["GET"])
def user_details_api(request):
    username = request.GET.get("username")

    try:
        con = get_db_connection()
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users1 WHERE username=%s", (username,))
            user = cur.fetchone()

        return Response({"user": user})

    except Exception as e:
        return Response({"error": str(e)})



@api_view(["GET"])
def user_page_api(request):
    username = request.GET.get("username")

    if not username:
        return Response({"error": "user required"})

    return Response({"success": "user page loaded", "username": username})


@api_view(["POST"])
def add_service_api(request):
    name = request.data.get("name")
    category = request.data.get("category")
    address = request.data.get("address")
    contact = request.data.get("contact")
    capacity = request.data.get("capacity")
    available = request.data.get("available")
    timings = request.data.get("timings")
    added_by = request.data.get("added_by")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO services
            (name, category, address, contact, capacity, available, timings, added_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, category, address, contact, capacity, available, timings, added_by))
        con.commit()

    return Response({"success": "Service added successfully"})


@api_view(["GET"])
def nearby_services_api(request):
    category = request.GET.get("category")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        if category:
            cur.execute(
                "SELECT * FROM services WHERE category=%s",
                (category,)
            )
        else:
            cur.execute("SELECT * FROM services")

        services = cur.fetchall()

    return Response({"services": services})



@api_view(["POST"])
def update_service_api(request):
    service_id = request.data.get("id")
    name = request.data.get("name")
    category = request.data.get("category")
    address = request.data.get("address")
    contact = request.data.get("contact")
    capacity = request.data.get("capacity")
    available = request.data.get("available")
    timings = request.data.get("timings")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE services
            SET name=%s,
                category=%s,
                address=%s,
                contact=%s,
                capacity=%s,
                available=%s,
                timings=%s
            WHERE id=%s
        """, (name, category, address, contact, capacity, available, timings, service_id))
        con.commit()

    return Response({"success": "Service updated successfully"})

@api_view(["POST"])
def report_issue_api(request):
    username = request.data.get("username")
    service_id = request.data.get("service_id")
    issue_type = request.data.get("issue_type")
    description = request.data.get("description")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO issue_reports
            (username, service_id, issue_type, description)
            VALUES (%s,%s,%s,%s)
        """, (username, service_id, issue_type, description))
        con.commit()

    return Response({"success": "Issue reported successfully"})


@api_view(["GET"])
def admin_view_issues_api(request):
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM issue_reports")
        issues = cur.fetchall()

    return Response({"issues": issues})


@api_view(["POST"])
def resolve_issue_api(request):
    issue_id = request.data.get("id")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE issue_reports SET status='Resolved' WHERE id=%s",
            (issue_id,)
        )
        con.commit()

    return Response({"success": "Issue resolved"})

@api_view(["POST"])
def submit_query_api(request):
    username = request.data.get("username")
    query = request.data.get("query")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_queries (username, query) VALUES (%s,%s)",
            (username, query)
        )
        con.commit()

    return Response({"success": "Query submitted"})


@api_view(["GET"])
def admin_view_queries_api(request):
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM user_queries")
        queries = cur.fetchall()

    return Response({"queries": queries})


@api_view(["POST"])
def reply_query_api(request):
    qid = request.data.get("id")
    reply = request.data.get("reply")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            UPDATE user_queries
            SET admin_reply=%s, status='Replied'
            WHERE id=%s
        """, (reply, qid))
        con.commit()

    return Response({"success": "Reply sent"})

@api_view(["POST"])
def change_service_status_api(request):
    service_id = request.data.get("id")
    status = request.data.get("status")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "UPDATE services SET status=%s WHERE id=%s",
            (status, service_id)
        )
        con.commit()

    return Response({"success": "Service status updated"})

@api_view(["POST"])
def rate_service_api(request):
    username = request.data.get("username")
    service_id = request.data.get("service_id")
    rating = request.data.get("rating")

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO ratings (username, service_id, rating) VALUES (%s,%s,%s)",
            (username, service_id, rating)
        )
        con.commit()

    return Response({"success": "Rating submitted"})


@api_view(["GET"])
def admin_view_ratings_api(request):
    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute("""
            SELECT 
                r.username,
                s.name AS shelter_name,
                r.rating
            FROM ratings r
            JOIN services s ON r.service_id = s.id
            ORDER BY r.id DESC
        """)
        ratings = cur.fetchall()

    return Response({"ratings": ratings})



@api_view(["GET"])
def user_my_issues_api(request):
    username = request.GET.get("username")

    if not username:
        return Response({"issues": []})

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT id, issue_type, status FROM issue_reports WHERE username=%s",
            (username,)
        )
        issues = cur.fetchall()

    return Response({"issues": issues})

@api_view(["GET"])
def user_my_queries_api(request):
    username = request.GET.get("username")

    if not username:
        return Response({"queries": []})

    con = get_db_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT id, query, admin_reply, status FROM user_queries WHERE username=%s ORDER BY id ASC",
            (username,)
        )
        queries = cur.fetchall()

    return Response({"queries": queries})
