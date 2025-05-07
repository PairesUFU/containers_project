from flask import Flask, request, jsonify
import os
import psycopg2
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'airlines')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASS = os.getenv('DB_PASS', 'password')
DB_PORT = os.getenv('DB_PORT', '5432')

def get_conn():
    return psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    if not user or user[1] != password:
        return jsonify({'error': 'Credenciais inválidas'}), 401
    user_id = user[0]
    session_key = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=2)
    ip = request.remote_addr
    cur.execute("INSERT INTO sessions (session_key, user_id, ip, expires_at) VALUES (%s, %s, %s, %s)",
                (session_key, user_id, ip, expires_at))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'session_key': session_key, 'expires_at': expires_at.isoformat()})

@app.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()
    session_key = data.get('session_key')
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE session_key=%s", (session_key,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Logout realizado com sucesso'})

@app.route('/validate_session', methods=['GET'])
def validate_session():
    session_key = request.args.get('session_key')
    ip = request.remote_addr
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT expires_at FROM sessions WHERE session_key=%s AND ip=%s", (session_key, ip))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row or row[0] < datetime.utcnow():
        return jsonify({'valid': False}), 401
    return jsonify({'valid': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)