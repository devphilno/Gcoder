from PySide6.QtWidgets import QApplication, QFileDialog, QComboBox, QPushButton, QTextEdit, QLineEdit,QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QSettings, QThread, Signal
from PySide6.QtGui import QTextCursor,QIcon
from pathlib import Path
import serial.tools.list_ports
import serial
import time
from GCoder_gui_ui import Ui_GCoder
from datetime import datetime

# ------------------- Setup Application -------------------
app = QApplication([])
settings = QSettings("MyCompany", "GCoderApp")
# Load UI
#ui_file = Path("GCoder_gui.ui")
#loader = QUiLoader()
#window = loader.load(str(ui_file))
#window.show()

#Set up UI
window = QMainWindow()
ui = Ui_GCoder()
ui.setupUi(window)
window.show()
window.setWindowIcon(QIcon("GCoder.ico"))
# Find widgets
sendbutton = window.findChild(QPushButton, "pbsend")
logwindow = window.findChild(QTextEdit, "telog")
gcodewindow = window.findChild(QLineEdit, "legcode")
com_combo = window.findChild(QComboBox, "cbCOM")
loadbutton = window.findChild(QPushButton, "pbload")
exportbutton = window.findChild(QPushButton, "pbexport")

# ------------------- Auto-Scrolling Log -------------------
def append_log(msg):
    logwindow.append(msg)
    logwindow.moveCursor(QTextCursor.End)
    logwindow.ensureCursorVisible()

# ------------------- COM Port Setup -------------------
last_port = settings.value("last_com_port", "")  # default empty string
ports = serial.tools.list_ports.comports()
for port in ports:
    com_combo.addItem(port.device)
if last_port and last_port in [p.device for p in ports]:
    index = com_combo.findText(last_port)
    com_combo.setCurrentIndex(index)

# Global serial object
ser = None

def open_serial():
    global ser
    if ser is None or not ser.is_open:
        selected_port = com_combo.currentText()
        ser = serial.Serial(selected_port, 115200, timeout=2)
        time.sleep(2)
        settings.setValue("last_com_port", selected_port)

# ------------------- Thread Management -------------------
active_threads = []

class GcodeSender(QThread):
    log_signal = Signal(str)

    def __init__(self, lines):
        super().__init__()
        self.lines = lines
        self._running = True

    def run(self):
        try:
            open_serial()
            for line in self.lines:
                if not self._running:
                    self.log_signal.emit("Thread stopped.")
                    break
                line = line.strip()
                if line == "" or line.startswith(";"):
                    continue
                self.log_signal.emit(f"Sending: {line}")
                ser.write((line + "\n").encode())
                ser.flush()
                while True:
                    response = ser.readline().decode("utf-8", errors="ignore").strip()
                    if response:
                        self.log_signal.emit(response)
                    if "ok" in response.lower() or not self._running:
                        break
        except Exception as e:
            self.log_signal.emit(f"Error: {e}")

    def stop(self):
        self._running = False

# ------------------- Button Handlers -------------------
def on_button_click():
    text = gcodewindow.text()
    if text and text[0].upper() == 'G'or text[0].upper() == 'M':
        gcodewindow.clear()
        sender = GcodeSender([text])
        sender.log_signal.connect(append_log)  # use auto-scrolling log
        sender.finished.connect(lambda: active_threads.remove(sender))
        active_threads.append(sender)
        sender.start()

def on_loadbutton_click():
    file_path, _ = QFileDialog.getOpenFileName(window, "Open G-code File", "", "G-code Files (*.gcode *.nc *.txt);;All Files (*)")
    if not file_path:
        return
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        sender = GcodeSender(lines)
        sender.log_signal.connect(append_log)  # use auto-scrolling log
        sender.finished.connect(lambda: active_threads.remove(sender))
        active_threads.append(sender)
        sender.start()
    except Exception as e:
        append_log(f"Error: {e}")

def on_exportbutton_click():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_name = f"export\log_{timestamp}.txt"
    file_path, _ = QFileDialog.getSaveFileName(
    window,
    "Save File",
    default_name,   # default filename with timestamp
    "Text Files (*.txt);;All Files (*)"
)
    if file_path and not file_path.endswith(".txt"):
        file_path += ".txt"
    if file_path:
        append_log(f"File will be saved to: {file_path}")
        text = logwindow.toPlainText()
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)

sendbutton.clicked.connect(on_button_click)
loadbutton.clicked.connect(on_loadbutton_click)
exportbutton.clicked.connect(on_exportbutton_click)
gcodewindow.returnPressed.connect(on_button_click)

# ------------------- Graceful Exit -------------------
def closeEvent(event):
    for thread in active_threads:
        thread.stop()
        thread.wait()
    event.accept()

window.closeEvent = closeEvent

# ------------------- Run App -------------------
app.exec()