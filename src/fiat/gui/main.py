import sys
from PySide2.QtWidgets import QApplication, QMainWindow


class gui(QMainWindow):
    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = gui()
    w.show()
    sys.exit(app.exec_())
    pass
