from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
import pyperclip
import sys
import json

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('configurator.ui', self)
        self.cfg = None
        self.current_cfg = None

        self.help = self.findChild(QtWidgets.QCommandLinkButton, "commandLinkButton")
        self.debug = self.findChild(QtWidgets.QCommandLinkButton, "commandLinkButton_2")
        self.open_config = self.findChild(QtWidgets.QPushButton, "pushButton")
        self.file_name_text = self.findChild(QtWidgets.QLabel, "label_3")
        self.action_name = self.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.action = self.findChild(QtWidgets.QComboBox, "comboBox")
        self.table = self.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.save_btn = self.findChild(QtWidgets.QPushButton, "pushButton_2")

        self.table.resizeColumnsToContents()

        self.help.clicked.connect(self.show_help)
        self.debug.clicked.connect(self.show_debug)
        self.open_config.clicked.connect(self.open_cfg)
        self.save_btn.clicked.connect(self.save_cfg)

        self.action.currentTextChanged.connect(self.setup_table)
        self.table.currentItemChanged.connect(self.setup_table)

        self.show()

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open config file", "", "Json files (*.json)", options=options)
        if file_name:
            return file_name
        else:
            return False

    def setup_table(self):
        index = self.action.currentIndex()

        indexes = [
            {
                "columns":[
                    "Name",
                    "Value",
                ],
                "rows":[
                    "Command"
                ]
            },
            {
                "columns": [
                    "Name",
                    "Value",
                ],
                "rows": [
                    "Path"
                ]
            },
            {
                "columns": [
                    "Name",
                    "Value",
                ],
                "rows": [
                    "Key"
                ]
            },
            {
                "columns": [
                    "Name",
                    "Value",
                ],
                "rows": [
                    "Sequence"
                ]
            },
            {
                "columns": [
                    "Name",
                    "Value",
                ],
                "rows": [
                    "Text"
                ]
            },
            {
                "columns": [
                    "Name",
                    "Value",
                ],
                "rows": [
                    "Function"
                ]
            }
        ]

        self.table.setColumnCount(len(indexes[index]["columns"]))
        self.table.setRowCount(len(indexes[index]["rows"]))

        self.table.setHorizontalHeaderLabels(indexes[index]["columns"])

        for i in range(len(indexes[index]["rows"])):
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(indexes[index]["rows"][i]))
            cell_item = self.table.item(i, 0)
            cell_item.setFlags(cell_item.flags() ^ Qt.ItemIsEditable)

    def error(self, title, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()

    def open_cfg(self):
        file_name = self.open_file_dialog()
        if file_name:
            self.cfg = file_name
        else:
            self.error("Error!", "Invalid file!")
            return

        file = open(self.cfg)
        self.current_cfg = file.read()
        file.close()

        self.ready()

        try:
            self.old_cfg = json.loads(self.current_cfg)
        except:
            self.error("Error!", "Unable to read old configuration!")
            self.old_cfg = {}

    def set_enable(self, state):
        self.table.setEnabled(state)
        self.action_name.setEnabled(state)
        self.action.setEnabled(state)

    def ready(self):
        if self.cfg:
            self.set_enable(True)
            name = self.cfg.split('/')
            name.reverse()
            self.file_name_text.setText(name[0])
            self.setup_table()
        else:
            self.set_enable(False)

    def new_action(self):
        actions = [
            {
                "call": "exec_cmd",
                "params": [
                    "cmd"
                ],
            },
            {
                "call": "playsound",
                "params": [
                    "path"
                ],
            },
            {
                "call": "press",
                "params": [
                    "key"
                ],
            },
            {
                "call": "combo",
                "params": [
                    "combo"
                ],
            },
            {
                "call": "type",
                "params": [
                    "text"
                ],
            },
            {
                "call": "exec_py",
                "params": [
                    "def"
                ],
            },
        ]

        action_name = self.action_name.text()
        action = actions[self.action.currentIndex()]["call"]
        params = {}

        full_action = {}

        for i in range(len(actions[self.action.currentIndex()]["params"])):
            try:
                value = str(self.table.item(i, 1).text())
                params[actions[self.action.currentIndex()]["params"][i]] = value
            except:
                params[actions[self.action.currentIndex()]["params"][i]] = ""

        valid_keys = [
            "alt",
            "alt_l",
            "alt_r",
            "backspace",
            "caps_lock",
            "cmd",
            "cmd_l",
            "cmd_r",
            "ctrl",
            "ctrl_l",
            "ctrl_r",
            "delete",
            "down",
            "end",
            "enter",
            "esc",
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
            "f12",
            "f13",
            "f14",
            "f15",
            "f16",
            "f17",
            "f18",
            "f19",
            "f20",
            "home",
            "insert",
            "left",
            "menu",
            "num_lock",
            "page_down",
            "page_up",
            "pause",
            "print_screen",
            "right",
            "scroll_lock",
            "shift",
            "shift_l",
            "shift_r",
            "space",
            "tab",
            "up",
        ]

        # check 1
        if action == "press":
            if params["key"] == "":
                self.error("Error!", "Invalid key!")
                return
            elif params["key"][:1] == ";":
                if params["key"][1:] in valid_keys:
                    pass
                else:
                    self.error("Error!", "Invalid key!")
                    return
            elif params["key"][:1] != ";":
                if len(params["key"]) != 1:
                    self.error("Error!", "Invalid key!")
                    return

        # check 2
        if action == "combo":
            combo = params["combo"]

            try:
                combo_ = combo.split("|")
            except:
                self.error("Error!", "Invalid keys sequence!")
                return

            if len(combo_) < 2:
                self.error("Error!", "Invalid keys sequence!")
                return

            for key in combo_:
                if key == "":
                    self.error("Error!", "Invalid key!")
                    return
                elif key[:1] == ";":
                    if key[1:] in valid_keys:
                        pass
                    else:
                        self.error("Error!", "Invalid key!")
                        return
                elif key[:1] != ";":
                    if len(key) != 1:
                        self.error("Error!", "Invalid key!")
                        return

        # check 3
        if action_name == "":
            self.error("Error!", "Invalid action name!")
            return

        full_action["call"] = action
        full_action["params"] = params

        return full_action, action_name

    def save_cfg(self):
        new_action, name = self.new_action()

        self.old_cfg[name] = new_action

        print(self.old_cfg)

        file = open(self.cfg, "w")
        file.write(json.dumps(self.old_cfg))
        file.close()


    def show_debug(self):
        msg = QtWidgets.QMessageBox()
        msg.setText(f"Debug: \n{self.cfg}\n{self.current_cfg}")
        msg.setWindowTitle("Debug")
        msg.exec_()

    def show_help(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setText("For help visit our github page: \nhttps://github.com/NVcoder24/NVcoder-stream-deck \n(link copied to clipboard)")
        msg.setWindowTitle("Help")
        pyperclip.copy('https://github.com/NVcoder24/NVcoder-stream-deck')
        msg.exec_()


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()