from flask import Flask, request, jsonify, session, redirect, url_for, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'admin'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

users = {'admin': {'password': 'admin'}}

messages = []

def check_authentication():
    return 'username' in session

@app.route('/')
def index():
    if check_authentication():
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        if username not in users:
            users[username] = {'password': data.get('password')}
            return redirect(url_for('login'))
        return render_template('register.html', message='Пользователь уже зарегистрирован')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('index'))
        return render_template('login.html', message='Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if not check_authentication():
        return jsonify({'message': 'Необходима аутентификация'}), 401
    data = request.json
    sender = session['username']
    receiver = data.get('receiver')
    message = data.get('message')
    if receiver in users:
        messages.append({'sender': sender, 'receiver': receiver, 'message': message})
        return jsonify({'message': 'Сообщение отправлено'}), 201
    else:
        return jsonify({'message': 'Пользователь не найден'}), 404

@app.route('/get_messages', methods=['GET'])
def get_messages():
    if not check_authentication():
        return jsonify({'message': 'Необходима аутентификация'}), 401
    receiver = session['username']
    user_messages = [msg for msg in messages if msg['receiver'] == receiver]
    return jsonify(user_messages)

@app.route('/upload', methods=['POST'])
def upload_file():
    if not check_authentication():
        return jsonify({'message': 'Необходима аутентификация'}), 401
    if 'file' not in request.files:
        return jsonify({'message': 'Файл не найден'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Файл не выбран'}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'Файл успешно загружен'}), 201

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    if not check_authentication():
        return jsonify({'message': 'Необходима аутентификация'}), 401
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
