import requests
import os
import sqlite3
import uuid
import validators
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtWidgets import QInputDialog

class CoreLogic:
    def __init__(self, console_stream):
        self.script_directory = os.path.dirname(os.path.realpath(__file__))
        self.logs_directory = os.path.join(self.script_directory, 'logs')
        #Create the logs directory if it doesn't exist
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)

        self.database_path = os.path.join(self.logs_directory, 'uptime_logs.db')
        self.urls = []
        self.console = console_stream
        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.database_path) as db:
            cursor = db.cursor()
            cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS uptime_logs (
                uuid TEXT PRIMARY KEY,
                timestamp TEXT,
                url TEXT,
                status TEXT,
                response_time REAL,
                status_code TEXT
            )
            '''
            )

    def log_status(self, url, status, response_time, status_code):
        with sqlite3.connect(self.database_path) as db:
            cursor = db.cursor()
            cursor.execute(
                '''
                INSERT INTO uptime_logs (uuid, timestamp, url, status, response_time, status_code)
                VALUES (?, datetime('now'), ?, ?, ?, ?)
                ''',
                (str(uuid.uuid4()), url, status, response_time, status_code)
            )
            cursor.connection.commit()

    def get_url_input(self):
        url, ok = QInputDialog.getText(None, "Input URL", "URL:")
        if ok and url and self.validate_url(url):
            return url
        return None

    def validate_url(self, url_input):
        if not validators.url(url_input):
            self.console.write("Invalid URL. Please enter a valid URL\n")
            return False
        return True

    def show_logs(self, url_input):
        with sqlite3.connect(self.database_path) as db:
            cursor = db.cursor()
            cursor.execute(
                '''
                SELECT * FROM uptime_logs WHERE url = ? ORDER BY timestamp DESC
                ''',
                (url_input,)
            )
            logs = cursor.fetchall()
            formatted_logs = []
            for log in logs:
                formatted_log = f"UUID: {log[0]}, TIMESTAMP: {log[1]}, URL: {log[2]}, STATUS: {log[3]}, RESPONSE TIME: {log[4]}, STATUS CODE: {log[5]}\n"
                formatted_logs.append(formatted_log)

            return formatted_logs

    def check_uptime(self):
        def check_single_url(url):
            try:
                response = requests.get(url)
                response_time = response.elapsed.total_seconds()
                status_code = str(response.status_code)
                self.console.write(f"URL: {url}, STATUS: {'UP' if response.ok else 'FAIL'}, RESPONSE TIME: {response_time}, STATUS CODE: {status_code}\n")
                self.log_status(url, "UP" if response.ok else "FAIL", response_time, status_code)
            except requests.RequestException as e:
                self.console.write(f"Error checking uptime for {url}: {e}\n")
                self.log_status(url, "FAIL", None, None)
            except Exception as e:
                self.console.write(f"Unexpected error for {url}: {e}\n")

        try:
            with ThreadPoolExecutor() as executor:
                executor.map(check_single_url, self.urls)
        except Exception as e:
            self.console.write(f"Error during concurrent uptime checks: {e}\n")
