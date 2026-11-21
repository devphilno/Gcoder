from PySide6.QtWidgets import (
    QApplication, QFileDialog, QComboBox, QPushButton,
    QTextEdit, QLineEdit, QMainWindow, QToolButton
)
from PySide6.QtCore import QSettings, QThread, Signal, QEvent, Qt, QObject, QTimer
from PySide6.QtGui import QTextCursor, QIcon, QAction
from pathlib import Path
import serial.tools.list_ports
import serial
import time
from GCoder_gui_ui import Ui_GCoder
from datetime import datetime
from punch_changer import PunchManager
from punch_setup_window import SetupWindow, InitialPositionDialog


# --------------- initialize PunchChanger
punch_api = PunchManager()


# ------ Set current punch changer position -------
# popup to set current position of punch changer
def show_current_position_popup(reject_message):
    dialog = InitialPositionDialog(window)
    if dialog.exec() == 1:
        selected_index = dialog.get_selected_position_index()

        punch_api.set_current_position(selected_index)

        append_log(f"Set starting position to {selected_index + 1} .")

        update_punch_dropdown()
    else:
        append_log(f"{reject_message}")





# ------------------- Setup Application -------------------
app = QApplication([])
settings = QSettings("MyCompany", "GCoderApp")

# Set up UI
window = QMainWindow()
ui = Ui_GCoder()
ui.setupUi(window)
window.show()
window.setWindowIcon(QIcon("GCoder.ico"))

QTimer.singleShot(0, lambda: show_current_position_popup("Setting start position aborted. Setting default value: position 1."))

# Find widgets
sendbutton = window.findChild(QPushButton, "pbsend")
logwindow = window.findChild(QTextEdit, "telog")
gcodewindow = window.findChild(QLineEdit, "legcode")
com_combo = window.findChild(QComboBox, "cbCOM")
loadbutton = window.findChild(QPushButton, "pbload")
exportbutton = window.findChild(QPushButton, "pbexport")
refresh_com_button = window.findChild(QToolButton, "tb_refresh_com") # tool button to refresh com-port list
test_increment_button = window.findChild(QPushButton, "pb_increment")  # testing if increment funktion works
punch_changer_button = window.findChild(QComboBox, "cb_PunchChanger")

setup_button = window.findChild(QAction, "mb_settings_PunchSetup") # Button in menubar to open setup menü
set_punch_position_button = window.findChild(QAction, "mb_settings_SetCurrentPunchPosition") # Botton in menubar to open popup to select current position
export_PunchSettings_button = window.findChild(QAction, "mb_file_export_PunchSettings")
import_PunchSettings_button = window.findChild(QAction, "mb_file_import_PunchSettings")



# ------------------- Command History -------------------
commandmem = []
history_index = len(commandmem)  # For Up/Down arrow navigation

# ------------------- Auto-Scrolling Log -------------------
def append_log(msg):
    logwindow.append(msg)
    logwindow.moveCursor(QTextCursor.End)
    logwindow.ensureCursorVisible()

# ------------------- COM Port Setup -------------------
last_port = settings.value("last_com_port", "")
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

# ------------------- COM Port Refresh -------------------
def refresh_com_ports(): #method to rescan Com ports
    current_selection = com_combo.currentText() # save current com selection
    com_combo.clear() # clear current list

    available_ports = serial.tools.list_ports.comports()
    for port in available_ports: # searching for available ports
        com_combo.addItem(port.device) # adds item for every detectet com port

    if current_selection and current_selection in [p.device for p in available_ports]: #checks if current selected port ist still in new list
        index = com_combo.findText(current_selection)
        com_combo.setCurrentIndex(index) # automaticly chooses the com port again

    append_log("COM ports rescanned and updated.")

#-------------------- Punch Changing Combo Box ------------------
def update_punch_dropdown():

    if punch_changer_button is not None:
        punch_changer_button.blockSignals(True)

        punch_changer_button.clear()

        # get list of mounted punches
        mounted_punches = punch_api.get_mounted_punches()

        # fill dropdown with punches
        for punch in mounted_punches:
            display_text = f"{punch['size']}mm (Pos {punch['pos']})"
            # adds installed punches to menu and puts position aas userdata
            punch_changer_button.addItem(display_text, punch['pos'])

        active_pos = punch_api.get_current_position() + 1

        # searches for active position
        index = punch_changer_button.findData(active_pos)
        if index != -1:
            punch_changer_button.setCurrentIndex(index)

        # unblocks signals
        punch_changer_button.blockSignals(False)

        
if punch_changer_button is not None:
    update_punch_dropdown()
    punch_changer_button.activated.connect(lambda index: on_punch_selected(index, punch_changer_button))

def sender_helper(lines):
    global history_index

    # only single commands are added to command history
    if isinstance(lines, str):
        commandmem.append(lines)
        history_index = len(commandmem)
        # converter needs list
        lines = [lines]


    converted_lines = punch_api.k_code_converter(lines, punch_api)  # use KConverter  to generate Gcode from K-commands
    sender = GcodeSender(converted_lines)
    sender.log_signal.connect(append_log)
    sender.finished.connect(lambda: active_threads.remove(sender))
    active_threads.append(sender)
    sender.start()

    update_punch_dropdown()


def on_punch_selected(index, combo_widget):

    if index < 0:
        return

    # get position number
    target_pos = combo_widget.itemData(index)

    if target_pos:
        # use k2 command
        gcode_command = f"K2 P{target_pos}"

        sender_helper(gcode_command)




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
    if text and text[0].upper() in ['G', 'M','K']:
        gcodewindow.clear()

        sender_helper(text)


def on_loadbutton_click():
    file_path, _ = QFileDialog.getOpenFileName(
        window, "Open G-code File", "",
        "G-code Files (*.gcode *.nc *.txt);;All Files (*)"
    )
    if not file_path:
        return
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        sender_helper(lines)

    except Exception as e:
        append_log(f"Error: {e}")

def on_exportbutton_click():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    default_name = f"export/log_{timestamp}.txt"
    file_path, _ = QFileDialog.getSaveFileName(
        window,
        "Save File",
        default_name,
        "Text Files (*.txt);;All Files (*)"
    )
    if file_path and not file_path.endswith(".txt"):
        file_path += ".txt"
    if file_path:
        append_log(f"File will be saved to: {file_path}")
        text = logwindow.toPlainText()
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)

def open_setup_dialog(): # method to open the setup window
    dialog = SetupWindow(punch_api, window) # creating setup window in RAM
    dialog.exec() # Open the window modally (blocks the main UI)
    update_punch_dropdown()
    append_log("Setup closed. Configuration updated.")

def open_export_punchsettings_dialog():
    punch_api.export_punch_settings(window)

def open_import_punchsettings_dialog():
    punch_api.import_punch_settings(window)
    update_punch_dropdown()
    append_log("Punch settings imported.")

def increment_s1(key):
    punch_api.punch_count(key)

sendbutton.clicked.connect(on_button_click)
loadbutton.clicked.connect(on_loadbutton_click)
exportbutton.clicked.connect(on_exportbutton_click)
gcodewindow.returnPressed.connect(on_button_click)

if refresh_com_button:
    refresh_com_button.clicked.connect(refresh_com_ports) # connecting com refresh button; if button clicked: refreshing com ports

if test_increment_button:
    test_increment_button.clicked.connect(lambda: increment_s1("S1"))

if setup_button: # checks if botton exists
    setup_button.triggered.connect(open_setup_dialog) # if botton clicked: setup menu opens

if export_PunchSettings_button:
    export_PunchSettings_button.triggered.connect(open_export_punchsettings_dialog)

if set_punch_position_button:
    set_punch_position_button.triggered.connect(lambda: show_current_position_popup("Operation aborted. Current position not changed."))

if import_PunchSettings_button:
    import_PunchSettings_button.triggered.connect(open_import_punchsettings_dialog)


# ------------------- Arrow Key Handling (Function-Based) -------------------
def arrow_key_handler(event):
    global history_index
    if event.key() == Qt.Key.Key_Up:
        if commandmem and history_index > 0:
            history_index -= 1
            gcodewindow.setText(commandmem[history_index])
        return True
    elif event.key() == Qt.Key.Key_Down:
        if commandmem and history_index < len(commandmem) - 1:
            history_index += 1
            gcodewindow.setText(commandmem[history_index])
        elif history_index == len(commandmem) - 1:
            history_index += 1
            gcodewindow.clear()
        return True
    return False

class FuncFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if arrow_key_handler(event):
                return True
        return super().eventFilter(obj, event)

# ------------------- Connect Event Filter to gcodewindow -------------------
arrow_filter = FuncFilter()          # Keep a persistent reference
gcodewindow.installEventFilter(arrow_filter)

# ------------------- Graceful Exit -------------------
def closeEvent(event):
    for thread in active_threads:
        thread.stop()
        thread.wait()
    event.accept()

window.closeEvent = closeEvent

# ------------------- Run App -------------------
app.exec()