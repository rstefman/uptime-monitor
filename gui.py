from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QToolBar, QTextEdit, QInputDialog
from PySide6.QtCore import QSize, QTimer
from script import CoreLogic
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.first_run = True
        self.setWindowTitle("Uptime Monitor")

        self.monitor_button = QPushButton("Run Monitor")
        self.monitor_button.setCheckable(True)
        self.monitor_button.clicked.connect(self.run_monitor)

        add_url_button = QPushButton("Add URL")
        add_url_button.setCheckable(False)
        add_url_button.clicked.connect(self.add_url)

        remove_url_button = QPushButton("Remove URL")
        remove_url_button.setCheckable(False)
        remove_url_button.clicked.connect(self.remove_url)

        check_logs_button = QPushButton("Check Logs")
        check_logs_button.setCheckable(False)
        check_logs_button.clicked.connect(self.check_logs)

        clear_console_button = QPushButton("Clear Console")
        clear_console_button.setCheckable(False)
        clear_console_button.clicked.connect(self.clear_console)

        toolbar = QToolBar()
        toolbar.addWidget(self.monitor_button)
        toolbar.addWidget(add_url_button)
        toolbar.addWidget(remove_url_button)
        toolbar.addWidget(check_logs_button)
        toolbar.addWidget(clear_console_button)
        self.addToolBar(toolbar)
        self.setFixedSize(QSize(800,600))

        self.timer = QTimer()

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.setCentralWidget(self.console)

        console_stream = ConsoleStream(self.console)
        self.core_logic = CoreLogic(console_stream)

        self.timer.timeout.connect(self.run_monitor)

    def run_monitor(self):
        if self.monitor_button.isChecked():
            if self.first_run:
                #Prompt the user for the delay only on the first run
                delay, user_accepted = QInputDialog.getInt(self, "Input Delay", "Input delay (ms):")

                if user_accepted:
                    self.timer.start(delay)
                    self.first_run = False  # Update the flag
                    self.core_logic.check_uptime()
            else:
                self.timer.start()
                self.core_logic.check_uptime()
        else:
            self.core_logic.console.write("Monitor stopped\n")
            self.timer.stop()

    def add_url(self):
        url = self.core_logic.get_url_input()
        if url is not None:
            self.core_logic.urls.append(url)

    def remove_url(self):
        url = self.core_logic.get_url_input()
        if url in self.core_logic.urls:
            self.core_logic.urls.remove(url)

    def check_logs(self):
        self.console.clear()
        url = self.core_logic.get_url_input()
        logs = self.core_logic.show_logs(url)
        for log in logs:
            self.core_logic.console.write(str(log))

    def clear_console(self):
        self.console.clear()

class ConsoleStream:
    def __init__(self, console):
        self.console = console

    def write(self, text):
        self.console.insertPlainText(text)

    def flush(self):
        pass

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.stdout = window.core_logic.console
sys.stderr = window.core_logic.console
app.exec()
