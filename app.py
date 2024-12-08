from flask import Flask, request, jsonify, make_response
import sqlite3
import bcrypt
import base64

app = Flask(__name__)

# 数据库初始化
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        nickname TEXT,
        comment TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# **1. POST /signup**
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"message": "Account creation failed", "cause": "required user_id and password"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, password, nickname) VALUES (?, ?, ?)', (user_id, hashed_password, user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"message": "Account creation failed", "cause": "already same user_id is used"}), 400
    finally:
        conn.close()

    return jsonify({"message": "Account successfully created", "user": {"user_id": user_id, "nickname": user_id}}), 200


if __name__ == '__main__':
    app.run(debug=True)
