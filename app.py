from flask import Flask, request, jsonify
import os
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
        conn = sqlite3.connect('database.db', timeout=2)  # 超时设置，防止sqlite卡住
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, password, nickname) VALUES (?, ?, ?)', (user_id, hashed_password, user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"message": "Account creation failed", "cause": "already same user_id is used"}), 400
    except Exception as e:
        print(f"Signup Error: {e}")
        return jsonify({"message": "Server error"}), 500
    finally:
        conn.close()

    return jsonify({"message": "Account successfully created", "user": {"user_id": user_id, "nickname": user_id}}), 200


# **2. GET /users/{user_id}**
@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        print("Authorization header not found")
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        auth_type, auth_credentials = auth.split(' ')
        decoded_credentials = base64.b64decode(auth_credentials).decode('utf-8')
        provided_user_id, provided_password = decoded_credentials.split(':')
        print(f"Auth provided_user_id: {provided_user_id}")
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({"message": "Authentication Failed"}), 401

    if provided_user_id != user_id:
        print(f"User {provided_user_id} tried to access {user_id}")
        return jsonify({"message": "Authentication Failed"}), 401

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE LOWER(user_id) = LOWER(?)', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        print(f"User {user_id} not found in database")
        return jsonify({"message": "No User found"}), 404

    user_id, password, nickname, comment = user
    return jsonify({
        "message": "User details by user_id",
        "user": {
            "user_id": user_id,
            "nickname": nickname if nickname else user_id,
            "comment": comment if comment else ''
        }
    }), 200


# **3. PATCH /users/{user_id}**
@app.route('/users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        auth_type, auth_credentials = auth.split(' ')
        decoded_credentials = base64.b64decode(auth_credentials).decode('utf-8')
        provided_user_id, provided_password = decoded_credentials.split(':')
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({"message": "Authentication Failed"}), 401

    if provided_user_id != user_id:
        print(f"User {provided_user_id} tried to update {user_id}")
        return jsonify({"message": "No Permission for Update"}), 403

    data = request.json
    nickname = data.get('nickname')
    comment = data.get('comment')

    if not nickname and not comment:
        return jsonify({"message": "User updation failed", "cause": "required nickname or comment"}), 400

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET nickname = ?, comment = ? WHERE user_id = ?', (nickname, comment, user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "User successfully updated", "user": {"nickname": nickname, "comment": comment}}), 200


# **4. POST /close**
@app.route('/close', methods=['POST'])
def close_account():
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        return jsonify({"message": "Authentication Failed"}), 401

    try:
        auth_type, auth_credentials = auth.split(' ')
        decoded_credentials = base64.b64decode(auth_credentials).decode('utf-8')
        user_id, password = decoded_credentials.split(':')
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({"message": "Authentication Failed"}), 401

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Account and user successfully removed"}), 200


# 监听端口
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
