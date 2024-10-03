import jwt
from datetime import datetime, timedelta
import time
from abc import ABC, abstractmethod
import logging
import mysql
import mysql.connector
import random
import time
from socketio import Client

sio = Client()
sio.connect('http://localhost:5000')            # подключение к серверу


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# вспомогательные классы:
class Battery:
    def get_charge(self):
        # Возвращает случайное значение заряда батареи от 0 до 100%
        return round(random.uniform(0, 100), 0)
class GPS:
    def __init__(self, model, type_):
        self.model = model
        self.type_ = type_

        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0
        self.compass = 0
    def get_location(self):
        # Возвращает случайные координаты (широта и долгота + высота) в допустимом диапазоне
        lat = round(random.uniform(-90, 90), 4)
        lon = round(random.uniform(-180, 180), 4)
        alt = round(random.uniform(0, 1000), 2)
        return (lat, lon, alt)
class Camera:
    n_cameras = 1

    def __init__(self, id, type_, zoom):
        self.id = id
        self.type_ = type_
        self.zoom = zoom
        self.video = 0

    def get_image(self):
        # Реализация метода для получения изображения
        print("Сделан снимок")

    def record_video(self):
        # Реализация метода для записи видео
        print("Сделана запись")
    def update(self):
        d_video = random.uniform(-10, 10)
        self.video += d_video
        return self.video

class MotorController:
    def start(self):
        # Метод для запуска моторов
        print("Моторы запущены")

    def stop(self):
        # Метод для остановки моторов
        print("Моторы остановлены")


# для системы контроля доступа

SECRET_KEY = '123456'
def get_secret_key():
    return SECRET_KEY
def generate_token(user_id):
    expiration_time = datetime.utcnow() + timedelta(seconds=5)
    token = jwt.encode({"user_id": user_id, "exp": expiration_time}, get_secret_key(), algorithm="HS256")
    return token

class Drone:
    tbl_DB_cols = [
        "serial_number",
        "n_rotors",
        "id",
        "battery_lvl",
        "latitude",
        "longitude",
        "altitude",
        "direction",
        "speed",
        "time"]

    def __init__(self, id, serial_number, camera: Camera, battery: Battery, gps: GPS, motor: MotorController, n_rotors=None, battery_lvl = None, latitude = None, longitude = None, altitude = None, direction = None,speed = None, time = None):
        # Инициализация всех необходимых компонентов дрона
        self.camera = camera
        self.battery = battery
        self.gps = gps
        self.motor = motor

        self.id = id
        self.serial_number = serial_number
        self.n_rotors = n_rotors

        self.battery_lvl = battery_lvl
        self.latitude = latitude
        self.longitude = longitude
        self.direction = direction
        self.speed = speed
        self.time = time

    def get_location(self):
        # Получение текущих координат с помощью GPS модуля
        return self.gps.get_location()
    def get_battery(self):
        # Получение текущего заряда батареи
        return self.battery.get_charge()
    def motor_start(self):
        # Запуск моторов
        return self.motor.start()

    def motor_stop(self):
        # Остановка моторов
        return self.motor.stop()
    def get_image(self):
        # Получения изображения
        return self.get_image()
    def record_video(self):
        # Запись видео
        return self.record_video()
    def insert_drone(self, token):
        pass
    def remove_drone(self):
        pass
    def find_by_id(self):
        pass

    def __str__(self):
        return f"порядковый номер={self.serial_number}, моторов={self.n_rotors}ID={self.id}"
# режим полета
class FlightMode:
    def apply(self, drone):
        # Реализация перехода в ручной режим
        print("Переход в ручной режим")
        for _ in range(5):
            # Выводит текущие координаты дрона каждые 1 секунду
            print(f"Текущая координата: {gps.get_location()}")
            time.sleep(1)

class FlightController:
    def __init__(self, drone: Drone, camera: Camera, flight_mode: FlightMode):
        # Инициализация контроллера полета с использованием дрона и камеры + режима полета
        self.drone = drone
        self.camera = camera
        self.flight_mode = flight_mode

    def start_flight(self):
        # Метод для начала полета
        battery_charge = self.drone.get_battery()    # Проверка заряда батареи
        print(f"Заряд: {battery_charge}%")
        if battery_charge > 10:
            # Если заряд больше 10%, то применяется выбранный режим полета и запускаются моторы
            self.flight_mode.apply(self.drone)
            self.drone.motor_start()
        else:
            # Если заряд недостаточен, выводится предупреждение
            print("Низкий заряд для полета")

class IDroneMapper(ABC):                             # картограф, добавлять дроны в базу
    def __init__(self, connection):
        self.connection = connection
    @abstractmethod
    def insert_drone(self, token, drone: Drone):
        pass

    @abstractmethod
    def remove_drone(self, drone: Drone):
        pass

    @abstractmethod
    def find_by_id(self, drone_id: int):
        pass

class MySQLiteDroneMapper(IDroneMapper):
    def set_secret_key(self, secret_key):
        self.__secret_key = secret_key

     # декодировать токен
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.__secret_key, algorithms=['HS256'])
            return payload["user_id"]        # субъект токена (пользователь, которого он идентифицирует)
        except jwt.ExpiredSignatureError as e:
            print(f"Истек токен: {e}")
            return
        except jwt.InvalidTokenError as e:
            print(f"Токен не валиден: {e}")

    def insert_drone(self, token, drone: Drone):            # добавить дрон
        user_id = self.verify_token(token)
        if user_id:
            logging.info(f"Получен запрос от user:{user_id} к добавлению дрона, разрешение получено")     # не выводит в консоль разрешение
        else:
            logging.info(f"Запрос отклонен")
            self.__drone.insert_drone()

        query_builder = QueryBuilder()
        query = query_builder.insert_into("tbl_DB", [
                "serial_number"
                "id" "time" "n_rotors"]).values(
                                drone.serial_number,
                                drone.id,
                                drone.time,
                                drone.n_rotors

        ).build()
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, query_builder())
        except mysql.connector.Error as e:
            logging.error(f"Ошибка при добавлении дрона в БД. {e}")
        self.connection.commit()
        drone.id = cursor.lastrowid

    def remove_drone(self, drone: Drone):               # удалить дрон
        query_builder = QueryBuilder()
        if drone:
            if drone.id:
                query = query_builder.delete("tbl_drones", drone.id).build()
                cursor = self.connection.cursor()
                logging.info(query)
                logging.info(query_builder())
                cursor.execute(query, query_builder())
                self.connection.commit()                      # зафиксировать изменения
                return None
            logging.warning("У дрона нет id!")
            return None
        logging.warning("Не передан дрон!")

    def find_by_id(self, drone_id):                  # найти по id
        query_builder = QueryBuilder()
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, serial_number FROM users WHERE id = ?")
        result = cursor.fetchone()                  # строкой
        if result:
            return Drone(*result)
        return None

# Паттерн Абстрактная фабрика
class DBFactory(ABC):                                       # базовый класс
    @abstractmethod
    def connect(self, path_to_db: str):
        pass
class MySQLiteDBFactory(DBFactory):
# установить соединение с сервером MySQL
    def connect(self, path_to_db: str):        # определяет метод connect(), используемый для подключения к серверу MySQL
        try:
            connection = mysql.connector.connect()
            print("Подключение к базе данных MySQL прошло успешно")  # подключение к бд успешно выполнено
        except mysql.connector.Error as e:
            print(f"Произошла ошибка '{e}'")     # произошла ошибка
        return connection

# Выполнение запроса для создания БД
def create_database(connection, query):     # функция + параметры (объект, запрос о создании БД)
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            print("База данных создана успешно")
        except mysql.connector.Error as e:
            print(f"Произошла ошибка '{e}'")

# необходимо подключиться к базе данных
def create_connection(self):
    try:
        connection = mysql.connector.connect()
        print("Подключение к базе данных MySQL прошло успешно")
    except mysql.connector.Error as e:
        print(f"Произошла ошибка '{e}'")
    return connection

# Паттерн Строитель
class QueryBuilder:                                          # для запросов
    def __init__(self):
        self._query = "-"
                                                           # методы-строители:
    def select(self, table, columns="*"):                       # выбор
        self._query = f"SELECT {columns} FROM {table}"
        return self

    def where(self, condition):                             # где, условие
        if not self.where_query:
            self._query = "WHERE" + condition
        else:
            self._query += f" AND {condition}"                    # и
        return self

    def order_by(self, columns):                                # упорядочить по
        self._query = f"ORDER BY {', '.join(columns)}"
        return self

    def builf(self):                                            # сборка
        query = f"{self.select_query} {self.where_query}"
        if self.where_query:
            query += f" {self.where_query}"
        if self.order_query:
            query += f" {self.order_query}"
        return query

class IDroneRepository(ABC):
    def __init__(self, connection):
            self.mapper = MySQLiteDroneMapper(connection)

    @abstractmethod
    def insert_drone(self, token, drone: Drone):
            pass

    @abstractmethod
    def remove_drone(self, drone: Drone):
            pass

    @abstractmethod
    def find_by_id(self, drone_id: int):
            pass

class MySQLiteIDroneRepository(IDroneRepository):
    def insert_drone(self, drone: Drone):
            self.mapper.insert_drone(drone)

    def remove_drone(self, drone: Drone):
            logging.info(f"remove_drone: {drone}")
            self.mapper.remove_drone(drone)

    def find_by_id(self, drone_id: int):
            drone_values = self.mapper.find_by_drone(drone_id)
            if drone_values:
                drone_dict = dict(zip(Drone.tbl_DB, drone_values))
                return Drone(**drone_dict)
            logging.warning(f"В таблице tbl_BD нет дрона с id = {drone_id}")
            return None


def send_telemetry():                               # передача данных телеметрии
    data = {
        'time': round(random.uniform(0, 24), 2),
        'speed': round(random.uniform(5, 20), 2),
        'battery': random.randint(50, 100),
        'signal': random.randint(-90, -50),
        'latitude': round(random.uniform(40, 50), 6),
        'longitude': round(random.uniform(20, 30), 6),
        'altitude': round(random.uniform(5, 20), 2),
        'direction': round(random.uniform(0, 360), 2)
 }
    sio.emit('telemetry', data)             # передача телеметрии на сервер
    time.sleep(1)


if __name__ == '__main__':

    battery = Battery()
    drone = Drone("001", "SN123123", "001", "Brushed DC", "ModelY", "m")
    gps = GPS("ModelY", "GPS II")
    camera = Camera("001", "HD", 10)
    motor = MotorController()
    flight_mode = FlightMode()
    flightcontroller = FlightController("123", "001", "m")

    print(battery.get_charge())
    print(gps.get_location())
    camera.update()
    motor.start()
    motor.stop()
    flight_mode.apply(drone)
    #flightcontroller.start_flight()                # не могу вызвать метод, не показывает заряд

    user_id = 123
    token = generate_token(user_id)

    logging.info(f"User {user_id} получил токен: {token}")
    logging.info(f"User {user_id} аутентифицирован")
    drone.insert_drone(token)           # не выходит в коносль разрешение на добавление дрона
    time.sleep(6)

    while True:
        send_telemetry()

    factory = MySQLiteDBFactory()
    connection = factory.connect(path_to_db='031024_drone.db')
    if connection:
        logging.info("Соединение используется")
        cursor = connection.cursor()            # идет ошибка

        cursor.execute("""
                CREATE DATABASE tbl_DB IF NOT EXISTS (
                                    SERIAL NUMBER, ID, TIME
                                    serial_number TEXT,
                                    n_rotors INTEGER,
                                    id TEXT,
                                    time DATATIME
                              )
                                """);

        # Данные для вставки в таблицу
        drone = {
           "serial_number": "SN123123",
           "n_rotors": 4,
            "id": "123",
            "time": 1
        }

        cursor.execute("""
                CREATE DATABASE tbl_DB1 IF NOT EXISTS (
                SERIAL NUMBER, ID, BATTERY_LVL, LATITUDE, LONGITUDE, ALTITUDE, DIRECTION, SPEED, TIME
                serial_number TEXT
                id TEXT,
                battery_lvl INTEGER,
                latitude REAL,
                longitude REAL,
                altitude REAL,
                direction REAL,
                speed INTEGER,
                time DATETIME
             )
           """)


        drone_0 = {}          #   Drone(**drone)

        query_builder = QueryBuilder()
        insert_into = (query_builder.insert_into("tbl_DB")).select(drone["serial_number", "id", "time"].build())
        insert_into = (query_builder.insert_into("tbl_DB1")).select(drone["serial_number", "latitude", "longitude", "altitude", "direction", "speed", "time"].build())
        logging.info(insert_into)

        # Подключение к базе данных MySQL

        connection = mysql.connector.connect('tbl_DB')

        try:
            drone_repository = MySQLiteDroneMapper(connection)
            drone_repository.insert_drone(drone_0)

            for drone in drone_repository.find_by_drone():
                logging.info(drone)

            drone_1 = drone_repository.find_by_drone(1)
            drone_repository.remove_drone(drone_1)
            logging.info("\n=============\n")
            for drone in drone_repository.find_by_drones():
                logging.info(drone)

        except mysql.connector.Error as e:
            logging.warning(f"Ошибка! {e}")


        cursor.close()                       # закрыть курсор
        connection.close()                   # закрыть соединение
        logging.info("Соединение закрыто")
    else:
        logging.info("Соединение не было установлено")


# строка 389 ошибка: Traceback (most recent call last) // что с этим делать?
# db не создаются
# пропадает информация о подключении к mysql, если включить сервер





