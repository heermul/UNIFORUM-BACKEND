from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import psycopg2

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        "postgresql://postgres:YOUR_PASSWORD@db.pxtbjwqhkcbpwvvugwxn.supabase.co:5432/postgres"
    )


@app.route("/")
def home():
    return "UNIFORUM Backend Running"


@app.route("/events", methods=["GET"])
def get_events():
    try:
        db = get_db_connection()
        cursor = db.cursor

        cursor.execute("SELECT * FROM events")
        rows = cursor.fetchall()

        data = []
        for e in rows:
            data.append({
                "id": e[0],
                "title": e[1],
                "forum": e[2],
                "event_date": str(e[3]),
                "event_time": e[4],
                "venue": e[5],
                "description": e[6],
                "status": e[7],
                "reason": e[8],
                "participants": e[9],
                "guests": e[10],
                "feedback": e[11],
                "images": e[12]
            })

        cursor.close()
        db.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/events_table")
def events_table():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events")
    data = cursor.fetchall()

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

    for e in data:
        html += f"""
        <tr>
            <td>{e['id']}</td>
            <td>{e['title']}</td>
            <td>{e['forum']}</td>
            <td>{e['event_date']}</td>
            <td>{e['venue']}</td>
            <td>{e['status']}</td>
        </tr>
        """

    html += "</table>"

    cursor.close()
    db.close()

    return html


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
        cursor = db.cursor(dictionary=True)

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