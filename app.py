from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import psycopg2
import psycopg2.extras
import os

DATABASE_URL = "postgresql://postgres.pxtbjwqhkcbpwvvugwxn:HeerMulchandani.25!?@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    return psycopg2.connect(
        DATABASE_URL,
        connect_timeout=30,
    )

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "UNIFORUM Backend Running"


@app.route("/events", methods=["GET"])
def get_events():
    try:
        db = get_db_connection()
        cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify([dict(row) for row in rows])

    except Exception as e:
        print("DB ERROR:", e)
        return jsonify({"error": "Database temporarily unavailable"}), 500

@app.route("/events_table")
def events_table():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()

        html = """
        <h2>UNIFORUM Events</h2>
        <table border="1" cellpadding="10">
        <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Forum</th>
            <th>Date</th>
            <th>Venue</th>
            <th>Status</th>
        </tr>
        """

        for e in rows:
            html += f"""
            <tr>
                <td>{e[0]}</td>
                <td>{e[1]}</td>
                <td>{e[2]}</td>
                <td>{e[3]}</td>
                <td>{e[5]}</td>
                <td>{e[7]}</td>
            </tr>
            """

        html += "</table>"

        cursor.close()
        db.close()

        return html

    except Exception as e:
        print("ERROR:", e)
        return f"Error: {str(e)}"


@app.route("/add_event", methods=["POST"])
def add_event():
    try:
        db = get_db_connection()
        cursor = db.cursor()

        data = request.get_json()

        query = """
        INSERT INTO events 
        (title, forum, event_date, event_time, venue, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data["title"],
            data["forum"],
            data["event_date"],
            data["event_time"],
            data["venue"],
            data["description"],
            "pending"
        )

        cursor.execute(query, values)
        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Event added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/approve_event/<int:event_id>", methods=["POST"])
def approve_event(event_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE events SET status='approved' WHERE id=%s",
        (event_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Event approved"})


@app.route("/reject_event/<int:event_id>", methods=["POST"])
def reject_event(event_id):

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE events SET status='rejected' WHERE id=%s",
        (event_id,)
    )

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Event rejected"})

@app.route("/update_status/<int:event_id>", methods=["POST"])
def update_status(event_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        data = request.get_json()
        new_status = data["status"]
        reason = data.get("reason")

        cursor.execute(
            "UPDATE events SET status=%s, reason=%s WHERE id=%s",
            (new_status, reason, event_id)
        )

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "Status updated successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})
        
@app.route("/delete_event/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "DELETE FROM events WHERE id=%s",
            (event_id,)
        )

        db.commit()

        cursor.close()
        db.close()

        return jsonify({"message": "Event deleted"})

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/add_past_event/<int:event_id>", methods=["POST"])
def add_past_event(event_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        data = request.get_json()

        participants = data.get("participants")
        guests = data.get("guests")
        feedback = data.get("feedback")
        images = data.get("images")  # should be JSON string

        cursor.execute("""
            UPDATE events
            SET participants=%s, guests=%s, feedback=%s, images=%s
            WHERE id=%s
        """, (participants, guests, feedback, images, event_id))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"message": "Past event data saved"})

    except Exception as e:
        return jsonify({"error": str(e)})
        
@app.route("/ping")
def ping():
    return "alive"

@app.route("/health")
def health():
    return jsonify({"status": "alive"})