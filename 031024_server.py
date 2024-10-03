from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'             # шифрование связи в сессии
socketio = SocketIO(app)

# построениe маршрута
@app.route('/')
def index():                                    # название главной страницы
    return render_template("index1.html")

@socketio.on('telemetry')
def handle_telemetry(data):                         # событие получения телеметрии
    logging.info(f"Получена телеметрия: {data}")
    emit('update_telemetry', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
