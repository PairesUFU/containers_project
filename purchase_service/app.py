from flask import Flask, request, jsonify
import os
import psycopg2
import uuid
from datetime import datetime

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'airlines')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

def get_conn():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

@app.route('/purchase', methods=['POST'])
def purchase():
    data = request.get_json()
    session_key = data.get('session_key')
    flight_id = data.get('flight_id')
    passengers = data.get('passengers', 1)
    conn = get_conn()
    cur = conn.cursor()
    # Valida sessão
    cur.execute("SELECT user_id FROM sessions WHERE session_key=%s AND expires_at>NOW()", (session_key,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'Sessão inválida ou expirada'}), 401
    user_id = row[0]
    # Cria reserva
    locator = str(uuid.uuid4())[:8]
    cur.execute("INSERT INTO reservations (user_id, flight_id, locator) VALUES (%s, %s, %s) RETURNING id", (user_id, flight_id, locator))
    reservation_id = cur.fetchone()[0]
    tickets = []
    for _ in range(passengers):
        ticket_no = str(uuid.uuid4())[:8]
        tickets.append(ticket_no)
        cur.execute("INSERT INTO tickets (reservation_id, ticket_number) VALUES (%s, %s)", (reservation_id, ticket_no))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'locator': locator, 'tickets': tickets})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)