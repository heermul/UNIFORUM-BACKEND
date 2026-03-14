from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host="mysql.railway.internal",
        user="root",
        password="ljhbWvJHRaipNkxLDVGfejWkNVVUxczS",
        database="railway",
        port=3306,
        autocommit=True
    )

db = get_db_connection()
cursor = db.cursor(dictionary=True)

@app.route("/")
def home():
    return "UNIFORUM Backend Running"


@app.route("/events", methods=["GET"])
def get_events():
    cursor.execute("SELECT * FROM events")
    data = cursor.fetchall()
    return jsonify(data)

@app.route("/events_table")
def events_table():

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
    return html

@app.route("/add_event", methods=["POST"])
def add_event():

    data = request.get_json()

    query = """
    INSERT INTO events (title, forum, event_date, venue, description)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        data["title"],
        data["forum"],
        data["event_date"],
        data["venue"],
        data["description"]
    )

    cursor.execute(query, values)

    return jsonify({"message": "Event added successfully"})


@app.route("/approve_event/<int:event_id>", methods=["POST"])
def approve_event(event_id):

    cursor.execute(
        "UPDATE events SET status='approved' WHERE id=%s",
        (event_id,)
    )

    return jsonify({"message": "Event approved"})


@app.route("/reject_event/<int:event_id>", methods=["POST"])
def reject_event(event_id):

    cursor.execute(
        "UPDATE events SET status='rejected' WHERE id=%s",
        (event_id,)
    )

    return jsonify({"message": "Event rejected"})


if __name__ == "__main__":
    app.run(debug=True)