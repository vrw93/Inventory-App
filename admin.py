from Core.Storage import Storage
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys, os

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        #Windows Setup
        self.setWindowTitle("Aplikasi Inventaris[Admin]")
        self.setGeometry(100, 100, 800, 600)
        
        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/admin.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage()

        #Post Setup
        self.setCentralWidget(self.ui)

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main()
    window.show()
    sys.exit(app.exec())