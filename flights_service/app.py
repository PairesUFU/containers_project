from flask import Flask, jsonify, request
import os
import psycopg2
from datetime import datetime

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'airlines')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

def get_conn():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

@app.route('/flights', methods=['GET'])
def get_flights():
    date_str = request.args.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Formato de data inválido, use YYYY-MM-DD'}), 400
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, flight_number, origin_id, destination_id, departure_time, arrival_time, price
        FROM flights
        WHERE DATE(departure_time) = %s
    """, (date,))
    flights = []
    for r in cur.fetchall():
        flights.append({
            'id': r[0],
            'flight_number': r[1],
            'origin_id': r[2],
            'destination_id': r[3],
            'departure_time': r[4].isoformat(),
            'arrival_time': r[5].isoformat(),
            'price': float(r[6])
        })
    cur.close()
    conn.close()
    return jsonify(flights)

@app.route('/search', methods=['POST'])
def search_flights():
    data = request.get_json()
    origin = data.get('origin_id')
    dest = data.get('destination_id')
    date_str = data.get('date')
    passengers = data.get('passengers', 1)
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Formato de data inválido'}), 400
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, flight_number, price
        FROM flights
        WHERE origin_id=%s AND destination_id=%s AND DATE(departure_time)=%s
        ORDER BY price ASC
        LIMIT 1
    """, (origin, dest, date))
    flight = cur.fetchone()
    cur.close()
    conn.close()
    if not flight:
        return jsonify({'flight': None})
    return jsonify({'flight_id': flight[0], 'flight_number': flight[1], 'price': float(flight[2]), 'passengers': passengers})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)