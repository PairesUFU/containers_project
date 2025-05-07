from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'airlines')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

def get_conn():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

@app.route('/airports', methods=['GET'])
def get_airports():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, code, name, city FROM airports")
    airports = [{'id': r[0], 'code': r[1], 'name': r[2], 'city': r[3]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(airports)

@app.route('/airports/<int:origin_id>/destinations', methods=['GET'])
def get_destinations(origin_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT a.id, a.code, a.name, a.city
        FROM flights f
        JOIN airports a ON f.destination_id = a.id
        WHERE f.origin_id = %s
    """, (origin_id,))
    dests = [{'id': r[0], 'code': r[1], 'name': r[2], 'city': r[3]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(dests)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)