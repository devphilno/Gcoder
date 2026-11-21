from pathlib import Path
import json
from PySide6.QtWidgets import QFileDialog, QMessageBox
import shutil


# ------------------- GCode Constants -----------------------
GCOM_SETEXTRREL     = "M83"         # Set Extruder to relative mode
GCOM_SETEXTRABS     = "M82"         # Set Extruder to absolute mode
GCOM_SETSPUNIT      = "M92 E"       # Set Steps per Unit
GCOM_GETCURPOS      = "M114"        # Get current position
GCOM_SETMAXFEED     = "M203 E"      # Set max feedrate
GCOM_DISCOLDEXRPREV = "M302 S0"     # Disable Cold Extrusion prevent
GCOM_GETCURSETT     = "M503"        # Get current settings


# ------------------- Punch-Class -------------------
# Class to define one single punch
class Punch:
    def __init__(self, size: int, pos: int = 7, n_punching: int = 0):
        self.size = size
        self.pos = pos
        self.nPunching = n_punching




# ------------------- Storage -------------------
# class to store and load Punch and revolver settings to/from JSON-file
class PunchStorage:
    def __init__(self):

        # setting path for directory to store json-file

        # filepath to store settings file in AppData folder or similar on Windows, Linux, and macOS
        # app_name = "GCoder"
        # config_dir = Path.home() / ".config" / app_name if os.name != 'nt' else Path(os.environ['APPDATA']) / app_name # configures pathname for saving files

        # filepath to store settings file in subfolder "settings" of current file path
        config_dir = Path(__file__).parent / "settings"

        # makes directory and ignores if directory already exists
        config_dir.mkdir(parents=True, exist_ok=True)


        # setting name of JSON-file and starting file structure
        self.json_file = config_dir / "punch_changer_settings.json"
        self._init_json()


    # method to start file structure
    def _init_json(self):

        # Creates an empty valid JSON structure with its own path if the file doesn't exist
        if not self.json_file.exists():
            # define initial data
            initial_data = {
                "file_path": str(self.json_file.resolve()),
                "magazine_settings": {}
            }
            # write initial_data to file
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)


    # method to load the current magazine from JSON-file
    def load_magazine(self):
        try:
            # if file doesn't exist return empty dictionary
            if not self.json_file.exists():
                return {}

            # opens JSON-file as Data
            with open(self.json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # getting "magazine_settings" from JSON-file as magazine_data; returning empty dictionary if no magazine_settings is in file
            magazine_data = data.get("magazine_settings", {})
            if not magazine_data:
                return {}

            # initialize magazine, fill it with punch instances
            magazine = {}
            for key, punch_data in magazine_data.items():
                # loop to generate punch object from every entry in the JSON and storing it in dictionary
                size = punch_data.get("size", 0)
                pos = punch_data.get("pos", 0)
                n_punching = punch_data.get("nPunching", 0)
                magazine[key] = Punch(size, pos, n_punching)
            return magazine

        # Returns empty dict if file is corrupted or unreadable
        except (json.JSONDecodeError, OSError):
            return {}


    # method to save a single punch to JSON-file
    def save_single_punch(self, key, punch):

        if punch is None:
            return False

        try:
            # Load existing data
            data = {"file_path": str(self.json_file.resolve()), "magazine_settings": {}}
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    # Keep the initial structure if file was empty/corrupted
                    except json.JSONDecodeError:
                        pass

            # Ensure the path is always updated/saved inside itself
            data["file_path"] = str(self.json_file.resolve())
            if "magazine_settings" not in data:
                data["magazine_settings"] = {}

            # Update or insert the single punch data
            data["magazine_settings"][key] = {
                "size": punch.size,
                "pos": punch.pos,
                "nPunching": punch.nPunching
            }

            # Write physical data back to file
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True

        except OSError:
            return False


    # Method to export punch settings as JSON-file
    def export_settings_as_json(self, parent_widget = None):
        source_path = self.json_file

        # display an error if file doesn't exists
        if not source_path.exists():
            QMessageBox.warning(parent_widget, "Export error", "No settings found.")
            return

        # let user choose file path with FileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "export punch settings as JSON",
            "revolver_settings.json",
            "JSON Dateien (*.json)"
        )

        # if file_path exists -> copies file with shutil
        if file_path:
            try:
                shutil.copy2(source_path, file_path)
                QMessageBox.information(parent_widget, "success", "Settings exported successfully!")
            except OSError as e:
                QMessageBox.critical(parent_widget, "Error", f"Export failed:\n{str(e)}")


    # method to import settings as JSON-file
    def import_settings(self, parent_widget = None):

        target_path = self.json_file

        # File dialog to open file
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget,
            "import punch settings",
            "",
            "JSON Dateien (*.json)"
        )

        # if user aborts filedialog abort the method
        if not file_path:
            return

        # asking for permission to overide current settings
        reply = QMessageBox.question(
            parent_widget,
            "Overwrite Settings?",
            "Are you sure you want to permanently overwrite your current settings with this file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # no is highlighted
        )

        # if user clicked "yes"
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # reading JSON-file
                with open(file_path, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)

                # checks if magazine_settings exists
                if "magazine_settings" not in import_data or not isinstance(import_data["magazine_settings"], dict):
                    QMessageBox.critical(parent_widget, "Import Error",
                                         "Invalid file structure: 'magazine_settings' section is missing.")
                    return

                # validating every punch
                magazine_settings = import_data["magazine_settings"]
                required_keys = {"size", "pos", "nPunching"}

                # initializing new dictionary
                fresh_magazine_dict = {}

                for punch_key, punch_fields in magazine_settings.items():
                    # checking if punches are dictionaries
                    if not isinstance(punch_fields, dict):
                        QMessageBox.critical(parent_widget, "Import Error", f"Invalid data format for punch item '{punch_key}'.")
                        return

                    # checks if at least all required kes are set)
                    if not required_keys.issubset(punch_fields.keys()):
                        missing = required_keys - punch_fields.keys()
                        QMessageBox.critical(parent_widget, "Import Error",
                                             f"Punch '{punch_key}' is missing required attributes: {', '.join(missing)}")
                        return

                    # generating a dictionary to override current dictionary
                    fresh_magazine_dict[punch_key] = Punch(
                        size = punch_fields.get("size", 0),
                        pos = punch_fields.get("pos", 0),
                        n_punching = punch_fields.get("nPunching", 0)
                    )

                # update file path
                import_data["file_path"] = str(target_path.resolve())

                # write new settings file
                with open(target_path, 'w', encoding='utf-8') as f:
                    json.dump(import_data, f, indent=4)

                return fresh_magazine_dict

            except (json.JSONDecodeError, OSError):
                QMessageBox.critical(parent_widget, "Import Error", "The selected file is corrupted or not a valid JSON file!")



    # method to save everything to JSON-file
    def save_all(self, magazine: dict):
        try:

            # Prepare the complete structure including the file path
            data = {
                "file_path": str(self.json_file.resolve()),
                "magazine_settings": {}
            }

            # loop to go through every item in dictionary
            for key, punch in magazine.items():
                data["magazine_settings"][key] = {
                    "size": punch.size,
                    "pos": punch.pos,
                    "nPunching": getattr(punch, 'nPunching', 0)
                }

            # Write physical data
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except OSError:
            return False




# ------------------- PunchChanger Class with KCodeConverter -------------------
class PunchChanger:
    def __init__(self):
        # Variables for Creality Ender 3 V3 SE
        self.E_STEPS_PER_MM = 424.9 # default Steps per unit value of the 3D-printer
        self.TOTAL_STEPS_PER_REV = 54400  # Steps needed for 1 revolution of the revolver
        self.TOTAL_STEPS_PER_POS = round(self.TOTAL_STEPS_PER_REV / 6)

        # 6 fixed positions for the punches
        self.STEPS_BETWEEN_POSITIONS = [
            self.TOTAL_STEPS_PER_REV / 6.0, # Abstand Pos. 1 zu 2
            self.TOTAL_STEPS_PER_REV / 6.0, # Abstand Pos. 2 zu 3
            self.TOTAL_STEPS_PER_REV / 6.0, # Abstand Pos. 3 zu 4
            self.TOTAL_STEPS_PER_REV / 6.0, # Abstand Pos. 4 zu 5
            self.TOTAL_STEPS_PER_REV / 6.0, # Abstand Pos.
            self.TOTAL_STEPS_PER_REV / 6.0
        ]
        self.current_absolute_steps = 0.0 # remembers current absolute step position

        # stores zero-based position of revolver (0-5)
        self.current_position = 0



    # method to run at program startup i.e. after connecting the printer
    @staticmethod
    def initial_setup():

        return [
            "; --- PunchChanger Initial Setup ---",
            GCOM_SETEXTRREL, # sets extruder to relative mode
            GCOM_DISCOLDEXRPREV, # disable Cold extrusion prevention
            "; ----------------------------------"
        ]


    # method to calculate needed steps to go to next position
    def calculate_steps(self, target_position: int):
        # transform target position to zero based value
        target = target_position - 1
        current = self.current_position

        # calculates shortest direction to next position (integer value between -3 to +3)
        difference = (target - current + 3) % 6 - 3

        # calculating needed steps with steps for step multiplied with difference
        needed_steps =  difference * self.TOTAL_STEPS_PER_REV / 6 # calculates needed steps

        needed_steps_int = round(needed_steps)

        return needed_steps_int

    def calculate_distance(self, target_position):
        target = target_position - 1
        current = self.current_position

        # calculates shortest direction to next position
        difference = (target - current + 3) % 6 - 3

        return difference



    # method to catch GCode command that starts with "K" and transforms it into G-Value based on configured data
    def convert_lines(self, input_lines, punch_changer_instance):

        # empty list for converted lines
        output_lines = []

        # check if there is more than one line
        show_line_no = len(input_lines) > 1

        for line_no, line in enumerate(input_lines, start=1):
            cleaned = line.strip()  # removing invisible chars

            # setting line no as prefix if more than one line
            prefix = f"; Line {line_no}: " if show_line_no else "; "

            # filter lowercase commands
            if cleaned.startswith('k'):
                output_lines.append(f"; {prefix} Ignoring: lowercase command '{cleaned}', use uppercase K")
                continue

            # filter only "K"-commands
            # checks whether the line starts with "K" and is not a comment
            if (cleaned.startswith('K')) and not cleaned.startswith(';'):

                # Split the parts in k_part and p_part and extract only numeric value
                parts = cleaned.split()
                if len(parts) < 2:
                    continue

                k_part = parts[0]
                p_part = parts[1]

                if not p_part.startswith('P'):
                    output_lines.append(f"; {prefix}Ignoring: expected P value, got '{p_part}' in '{cleaned}'")
                    continue

                # convert everything after the letter to an integer
                try:
                    k_num = int(k_part[1:])
                    p_num = int(p_part[1:])
                except ValueError:
                    output_lines.append(f"; {prefix}Ignoring: invalid command: '{cleaned}'")
                    continue


                # logic for K1 command (change punch by punch size)
                if k_num == 1:
                    size = p_num

                    # gets punch key by size
                    key = punch_changer_instance.get_key(size, "size")

                    # checks if key exists and if attribute value exists
                    if key is not None:
                        pos_value = punch_changer_instance.get_value(key, "pos")

                        if pos_value is not None:
                            target_pos = int(pos_value)
                        else:
                            output_lines.append(f";{prefix}Position value for key {key} is None/missing")
                            continue

                        # checks if position value is between 1 and 6; if 7 -> not mounted
                        if target_pos == 7:
                            output_lines.append(f";{prefix} punch not mounted")
                            continue
                        elif not (1 <= target_pos <= 6):
                            output_lines.append(
                                f";{prefix} Invalid position {target_pos} configured for punch size {size}mm (key {key}), expected 1-6 or 7")
                            continue
                    else:
                        output_lines.append(f";{prefix} punch size {size}mm not found")
                        continue


                # logic for K2 command (change punch by punch position)
                elif k_num == 2:
                    target_pos = p_num

                    # checks if position is between 1 and 6
                    if not (1 <= target_pos <= 6):
                        output_lines.append(f";{prefix} Ignoring: Invalid position K2 P{target_pos}")
                        continue

                else:
                    output_lines.append(f";{prefix} Ignoring: unknown command K{k_num} (only K1 and K2 supported)")
                    continue

                # gets needed steps and converts it to integer
                distance = self.calculate_distance(target_pos)*-1  #-1 to change direction of rotation to match hardware




                # gets target mm for the command to turn the extruder
                #target_mm = round(needed_steps / self.E_STEPS_PER_MM, 4) # calculates mm for GCode-command

                # Getting information for log
                current_punch_key = punch_changer_instance.get_key(target_pos, "pos")
                current_punch_size = punch_changer_instance.get_value(current_punch_key, "size")
                if current_punch_size == 0:
                    current_punch_size = "not set"
                from_pos = self.current_position + 1

                positions = self.TOTAL_STEPS_PER_POS

                # adding GCode command to output_lines
                output_lines.append(GCOM_SETEXTRREL) # set extruder to relative mode
                output_lines.append(GCOM_DISCOLDEXRPREV) # disable Cold extrusion prevent
                output_lines.append(f"{GCOM_SETSPUNIT}{positions}")
                output_lines.append(f"{GCOM_SETMAXFEED}2")
                output_lines.append(f"G1 E{distance} F500 ; changed from position K{from_pos} to K{target_pos} ( traveled {distance} positions), current punch size: {current_punch_size}mm") # generates gcode command

                self.current_position = target_pos - 1 # sets new position

            else:
                output_lines.append(line)
        return output_lines
    
    def set_current_revolver_pos(self, pos):
        # index is zero-based
        if 0 <= pos <= 5:
            self.current_position = pos
            return True
        return False


# ------------------- Revolver Class -------------------
# Runtime punch storage (faster loading times compared to loading every item from JSON)
class Revolver:
    def __init__(self):
        self.MAGAZINE = {
            'S1': Punch(1, 5, 10),
            'S2': Punch(2, 3),
            'S3': Punch(3, 2),
            'S4': Punch(4, 6),
            'S5': Punch(5, 4),
            'S6': Punch(6, 1),
            'S8': Punch(8)
        }

    # get and set methods to change values of punch magazine
    def get_punch_value(self, key, attribute):
        punch_object = self.MAGAZINE.get(key)

        if punch_object:
            return getattr(punch_object, attribute, None)

        return None

    def get_punch_key(self, value, attribute):
        for key, punch_object in self.MAGAZINE.items():
            if hasattr(punch_object, attribute) and getattr(punch_object, attribute) == value:
                return key

        return None

    def get_punch(self, key):
        if key in self.MAGAZINE:
            return self.MAGAZINE[key]
        return None


    def increment_punch_count(self, key):
        if key in self.MAGAZINE:
            punch = self.MAGAZINE[key]
            punch.nPunching = getattr(punch, 'nPunching', 0) + 1 # adds 1 to punch counter
            return True
        return False


    def set_punch(self, key: str, pos: int, reset_counter: bool): # set method for all parameters of punch
        if key in self.MAGAZINE:
            punch = self.MAGAZINE[key]
            punch.pos = pos
            if reset_counter: # checks if reset counter is true
                punch.nPunching = 0 # resets punch counter
            return True
        return False

    # method to override entire magazine
    def overwrite_magazine(self, fresh_magazine_dict):
        self.MAGAZINE.clear()  # deletes old data
        self.MAGAZINE.update(fresh_magazine_dict)  # copies objects to the magazine



# ------------------- Punch Manager -------------------
# class provides instances of all needed classes and provides funktions to use and interact with the Punch Changer.
class PunchManager:
    def __init__(self):
        self._revolver = Revolver() # instance of Revolver class
        self._storage = PunchStorage() # instance of revolver Storage class (JSON)
        self._pchanger = PunchChanger()

        saved_data = self._storage.load_magazine()

        if saved_data:
            self._revolver.MAGAZINE.clear()
            self._revolver.MAGAZINE = saved_data # if DB is filled data is stored into Magazine of revolver
        else:
            self._storage.save_all(self._revolver.MAGAZINE) # if JSON ist new or just empty default values are saved



    # ***** API endpoints *****
    # method to configure settings inside the printer to work with Punch changer
    def punch_changer_setup(self):
        self._pchanger.initial_setup()

    def override_entire_magazine(self, new_magazine):
        self._revolver.overwrite_magazine(new_magazine)


    # ---- Get-Methods ----
    # method to get specific value of punch by key
    def get_value(self, prime_key, attribute):
        return self._revolver.get_punch_value(prime_key, attribute)

    # Method to get Key by position of punch
    def get_key(self, value, attribute):
        return self._revolver.get_punch_key(value, attribute)

    # Method to get a Punch object
    def get_punch_obj(self, key):
        return self._revolver.get_punch(key)

    # Method to get whole MAGAZINE dictionary
    def get_all_punches(self):
        return self._revolver.MAGAZINE

    # method to get a list of all mounted punches
    def get_mounted_punches(self):
        mounted_punches = []

        for position in range(1,7):
            key = self.get_key(position, "pos")
            if key is not None:
                size = self.get_value(key, "size")

                if size and size != 0:
                    mounted_punches.append({
                        "key": key,
                        "size": size,
                        "pos": position
                    })

        return mounted_punches

    def get_current_position(self):
        return self._pchanger.current_position



    # ---- Conversion Methods ----
    def k_code_converter(self, lines, punch_changer_instance):
        return self._pchanger.convert_lines(lines, punch_changer_instance)



    # ---- Setter and save Methods ----
    # Sets punch settings for single Punch and saves them to DB if setting in dictionary was successful
    def set_punch_settings(self, punch_key: str, new_pos: int, reset_counter: bool):
        success = self._revolver.set_punch(punch_key, new_pos, reset_counter)
        if success:
            punch_obj = self._revolver.get_punch(punch_key)
            self._storage.save_single_punch(punch_key, punch_obj) # saves only changed punch settings
        return success

    # Sets punch only into dictionary. DOESTN'T saves it to DB
    def set_punch_memory_only(self, punch_key: str, new_pos: int, reset_counter: bool):
        return self._revolver.set_punch(punch_key, new_pos, reset_counter)

    # Saves whole Dictionary to DB
    def save_all_to_disk(self):
        self._storage.save_all(self._revolver.MAGAZINE)

    # increments punch count by one
    def punch_count(self, key):
        if self._revolver.increment_punch_count(key):
            punch_obj = self._revolver.get_punch(key)
            self._storage.save_single_punch(key, punch_obj)
            return True
        return False

    # ---- Import/export methods ----
    # method to export settings file (JSON)
    def export_punch_settings(self, parent_widget ):
        self._storage.export_settings_as_json(parent_widget)

    # method to import settings file (JSON)
    def import_punch_settings(self , parent_widget):
        fresh_magazine_dict = self._storage.import_settings(parent_widget)
        if fresh_magazine_dict is not None:
            self._revolver.overwrite_magazine(fresh_magazine_dict)
            QMessageBox.information(parent_widget, "Success", "Settings have been successfully imported and loaded!")
            return True
        return False

    # method to set current position
    def set_current_position(self, pos ):
        return self._pchanger.set_current_revolver_pos(pos)


