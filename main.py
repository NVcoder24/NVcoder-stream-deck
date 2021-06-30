from PyQt5 import QtWidgets, uic
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('configurator.ui', self)

        self.gen_button = self.findChild(QtWidgets.QPushButton, "pushButton")
        self.table = self.findChild(QtWidgets.QTableWidget, "tableWidget")
        self.columns = self.findChild(QtWidgets.QSpinBox, "spinBox")
        self.rows = self.findChild(QtWidgets.QSpinBox, "spinBox_2")
        self.filename = self.findChild(QtWidgets.QLineEdit, "lineEdit")
        self.baudrate = self.findChild(QtWidgets.QComboBox, "comboBox")
        self.rows_pins = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.row_pin_select = self.findChild(QtWidgets.QSpinBox, "spinBox_4")
        self.cols_pins = self.findChild(QtWidgets.QListWidget, "listWidget_2")
        self.col_pin_select = self.findChild(QtWidgets.QSpinBox, "spinBox_3")

        self.table.setColumnCount(1)
        self.table.setRowCount(1)

        self.gen_button.clicked.connect(self.generate)

        self.columns.valueChanged.connect(self.change_columns)
        self.rows.valueChanged.connect(self.change_rows)

        self.rows_pins.doubleClicked.connect(self.changed_row)
        self.cols_pins.doubleClicked.connect(self.changed_col)

        self.current_row = 0
        self.current_col = 0

        self.change_pins()

        self.show()

    def changed_row(self):
        sel_items = self.rows_pins.selectedItems()

        for item in sel_items:
            item.setText(str(self.row_pin_select.value()))

    def changed_col(self):
        sel_items = self.cols_pins.selectedItems()

        for item in sel_items:
            item.setText(str(self.col_pin_select.value()))

    def change_columns(self):
        self.table.setColumnCount(self.columns.value())
        self.change_pins()

    def change_rows(self):
        self.table.setRowCount(self.rows.value())
        self.change_pins()

    def change_pins(self):
        self.setup_lists(self.table.rowCount(), self.table.columnCount())

    def setup_lists(self, rows, cols):
        self.rows_pins.clear()
        self.cols_pins.clear()

        for row in range(rows):
            self.rows_pins.addItem(QtWidgets.QListWidgetItem(f'pin for row {row + 1}'))

        for col in range(cols):
            self.cols_pins.addItem(QtWidgets.QListWidgetItem(f'pin for column {col + 1}'))

    def get_table_content(self):
        result = []

        for row in range(self.table.rowCount()):
            result.append([])
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item is not None:
                    result[row].append(item.text())
                else:
                    return False

        return result

    def error(self, title, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()

    def info(self, title, text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.exec_()

    def get_pins(self):
        rows_pins, cols_pins = [], []

        for row in range(self.rows_pins.count()):
            item = self.rows_pins.item(row).text()
            try:
                int(item)
                rows_pins.append(item)
            except:
                return False

        for col in range(self.cols_pins.count()):
            item = self.cols_pins.item(col).text()
            try:
                int(item)
                cols_pins.append(item)
            except:
                return False

        return [rows_pins, cols_pins]

    def hexaKeys(self, matrix):
        matrix_new = []

        for item in matrix:
            lst = []
            for i in item:
                lst.append(f"'{i}'")
            matrix_new.append(','.join(lst) + ",")

        return "\n  " + "\n  ".join(matrix_new) + "\n"

    def pins_format(self, pins):
        return ",".join(pins)

    def format_code(self, rows, cols, matrix, cols_pins, rows_pins):
        code = """
#include <Keypad.h>
const byte ROWS = """ + str(rows) + """; 
const byte COLS = """ + str(cols) + """; 

char hexaKeys[ROWS][COLS] = {
  """ + self.hexaKeys(matrix) + """
};

byte rowPins[COLS] = {""" + self.pins_format(rows_pins) + """}; 
byte colPins[ROWS] = {""" + self.pins_format(cols_pins) + """}; 

Keypad customKeypad = Keypad(makeKeymap(hexaKeys), rowPins, colPins, ROWS, COLS); 

void setup(){
  Serial.begin(""" + self.baudrate.currentText() + """);
}

void loop(){
  char customKey = customKeypad.getKey();

  if (customKey){
    Serial.println(customKey);
  }
}
"""

        return code

    def generate(self):
        table_content = self.get_table_content()
        pins = self.get_pins()

        # check 1
        if not table_content:
            self.error("Error!", "check values in table again!")
            return
        else:
            pass

        # check 2
        if not pins:
            self.error("Error!", "illegal pins values!")
            return
        else:
            pass

        # check 3
        checked_pins = []
        for i in pins:
            for item in i:
                if item in checked_pins:
                    self.error("Error!", "check pins values again!")
                    return
                elif int(item) < 2:
                    self.error("Error!", "check pins values again!")
                    return
                else:
                    checked_pins.append(item)

        # check 4
        if self.filename.text() == "":
            self.error("Error!", "bad file name!")
            return

        # compiling
        code = self.format_code(self.rows_pins.count(),
                                self.cols_pins.count(),
                                table_content,
                                pins[0],
                                pins[1]
                                )

        file = open(self.filename.text(), "w")
        file.write(code)
        file.close()

        self.info("Complete!", f"File was saved as {self.filename.text()}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()