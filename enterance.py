# enterance.py 程序入口
import sys
from PyQt5.QtWidgets import QApplication
from main_window import CoordinateConverter

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoordinateConverter()
    ex.show()
    sys.exit(app.exec_())