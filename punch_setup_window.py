from PySide6.QtWidgets import QDialog, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QCheckBox, QMessageBox, QDialogButtonBox, QPushButton #Import UI elements für QT




# ------------------- Setup Window -------------------
# generates a dynamic setup dialog based on current punch values
class SetupWindow(QDialog):
    def __init__(self, punch_manager_instance,parent=None):
        super().__init__(parent) # Call the parent class to initialize window

        self.punch_manager_instance = punch_manager_instance

        self.setWindowTitle("punch-phanger-setup")
        self.setMinimumWidth(450) # sets minimum width

        self.main_layout = QVBoxLayout(self) # main layout to stack punch configurations vertically

        self.main_layout.setSpacing(15)  # spacing between rows
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # spacing to window border

        self.widgets = {} # dictionary to store references to inputs for retrieval during save
        self.previous_values = {} # saving previous value if user clicks no in duplicate messagebox

        total_items = len(punch_manager_instance.get_all_punches()) # counts total number of items

        for index, (key, punch) in enumerate(punch_manager_instance.get_all_punches().items()): # uses api to get punches; iterates through the dictionary to build dynamic Ui and sets index of elements to current number
            row_layout = QHBoxLayout() # horizontal layout
            row_layout.setSpacing(4)  # horizontal spacing per row

            lbl_name = QLabel(f"<b>Punch {key}</b> (size: {punch.size}mm):") # create label to show identifier
            lbl_position = QLabel("Position:") #Label for pos
            cb_pos = QComboBox() # new textbox as dropdown
            cb_pos.addItems(["1", "2", "3", "4", "5", "6", "7"]) # setting options for dropdown
            cb_pos.setCurrentText(str(punch.pos)) # sets current dropdown value to current punch position

            lbl_count = QLabel(f"Punch count: {punch.nPunching}") # displays current number of punch cycles of that punch
            cb_reset = QCheckBox("Reset") # generates check box for resetting punch count

            # filling row_layout (from left to right)
            row_layout.addWidget(lbl_name) # placing label with name and size of the punch
            row_layout.addStretch(1) # strech spacer
            row_layout.addWidget(lbl_position) # placing label for Position
            row_layout.addWidget(cb_pos) # placing textbox for position
            row_layout.addSpacing(15) # fixed spacer
            row_layout.addWidget(lbl_count) # placing label for current punch count
            row_layout.addWidget(cb_reset) # placing checkbox for resetting punch count

            self.main_layout.addLayout(row_layout) # places filled row into main layout

            if index < total_items - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)  # select line as shape
                line.setFrameShadow(QFrame.Shadow.Sunken) # sunken look
                self.main_layout.addWidget(line)


            # store references mapped by the punch key for saving
            self.widgets[key] = {
                'cb_pos': cb_pos,
                'cb_reset': cb_reset
            }

            self.previous_values[key] = str(punch.pos) # save current value
            cb_pos.currentTextChanged.connect(lambda text, k=key: self.resolve_duplicate_slots(k, text)) # sends changed value to duplicate checker method; lambda mini function grabs name of punch thats value changed

        self.button_box = QDialogButtonBox() # creating empty botton box

        self.button_box.addButton(QDialogButtonBox.StandardButton.Save) # adding standard save button to bnt-box
        self.button_box.addButton(QDialogButtonBox.StandardButton.Cancel) # adding standard cancel button to bnt-box

        self.button_box.accepted.connect(self.save_and_close)  # if save is clicked -> save method
        self.button_box.rejected.connect(self.reject)  # if cancel is clicked -> cancel (reject method)

        self.main_layout.addSpacing(10) # spacing between elements and buttons
        self.main_layout.addWidget(self.button_box) # add buttons to main layout

    def resolve_duplicate_slots(self, changed_key, new_value): # if 1-6 is already taken, the other pos is switched to 7
        if new_value == "7": # If value already "7" no check is needed
            self.previous_values[changed_key] = new_value # updates the tracker
            return

            # Loop through all other dropdowns to find a duplicate
        for key, item in self.widgets.items():
            if key == changed_key:
                    continue


            if item['cb_pos'].currentText() == new_value: # found duplicat
                reply = QMessageBox.question(
                     self,
                    "Slot Overwrite Confirmation",
                    f"Slot K{new_value} is already occupied by Punch {key}.\n\n"
                    f"Do you really want to move Punch {changed_key} to Slot K{new_value} and overwrite it?\n"
                    f"Punch {key} will be set as not installed!",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No  # Default button highlight
                ) # Open a standard confirmation popup dialog

                if reply == QMessageBox.StandardButton.Yes:  # if User clicked "Yes" -> set duplicate slot to 7
                    item['cb_pos'].blockSignals(True)  # blocking signals from button to prevent recursion loop
                    item['cb_pos'].setCurrentText("7")  # set other item to 7
                    item['cb_pos'].blockSignals(False)  # enable signals from button again


                    self.previous_values[key] = "7" # Updates Tracker of previous element
                    self.previous_values[changed_key] = new_value # updates Tracker of new element
                else: # User clicked "No" -> set old value back -> other value ist not overwritten
                    self.widgets[changed_key]['cb_pos'].blockSignals(True) # blocking signals from button to prevent recursion loop
                    self.widgets[changed_key]['cb_pos'].setCurrentText(self.previous_values[changed_key]) # sets Value back to the previous value
                    self.widgets[changed_key]['cb_pos'].blockSignals(False)# enable signals from button again

                return


        self.previous_values[changed_key] = new_value # If no duplicates were found, simply update the tracking dictionary



    def save_and_close(self):
        for key in self.punch_manager_instance.get_all_punches().keys(): # Loop through all configured punches in the magazine
            new_pos = int(self.widgets[key]['cb_pos'].currentText() ) # Get values from the GUI widgets stored in our dictionary
            reset_counter = self.widgets[key]['cb_reset'].isChecked() # get boolian for resetting punch count

            self.punch_manager_instance.set_punch_memory_only(key, new_pos, reset_counter) # Use the new setter method to set data in ram

        self.punch_manager_instance.save_all_to_disk() # saves entire dictionary to disc

        # Close the dialog and signal success to the main window
        self.accept()


class InitialPositionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("define current punch position")
        self.setModal(True)

        layout = QVBoxLayout()

        self.label = QLabel("Please select the position that is currently ready for punching \n (this punch is pointing straight down).")
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(400)
        layout.addWidget(self.label)

        self.combo_box = QComboBox()

        for i in range(1, 7):
            display_text = f"Position {i}"
            internal_value = i - 1
            self.combo_box.addItem(display_text, internal_value)

        layout.addWidget(self.combo_box)

        self.btn_confirm = QPushButton("set position")
        self.btn_confirm.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirm)

        self.setLayout(layout)

    def get_selected_position_index(self):

        return self.combo_box.currentData()

