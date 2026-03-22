from Core.Storage import Storage
from PySide6.QtWidgets import (QMainWindow, QApplication, QAbstractItemView, QSpinBox,
QTableWidgetItem, QDialog, QVBoxLayout, QInputDialog, QMessageBox)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QSettings
from PySide6.QtGui import QIcon
import sys, os

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        #Variable
        self.itemTotals = {}

        #Windows Setup
        self.setWindowTitle("Aplikasi Inventaris[Admin]")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(self.resource_path("Assets/icon.png")))
        
        #Settings
        self.settings = QSettings("VrwDev", "Inventory_App")

        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/admin.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage()

        #Reference
        self.tableP = self.ui.findChild(type(self.ui.PeminjamTable), "PeminjamTable")
        self.searchBarP = self.ui.findChild(type(self.ui.CariPeminjam), "CariPeminjam")
        self.tableI = self.ui.findChild(type(self.ui.ItemTable), "ItemTable")
        self.addBtn = self.ui.findChild(type(self.ui.TambahItemBtn), "TambahItemBtn")
        self.delBtn = self.ui.findChild(type(self.ui.HapusItemBtn), "HapusItemBtn")
        self.themeSwitcher = self.ui.findChild(type(self.ui.ThemeSwitcher), "ThemeSwitcher")

        #Connect Thing
        self.searchBarP.textChanged.connect(self.SearchBorrower)
        self.tableP.itemClicked.connect(self.selectBorrower)
        self.addBtn.clicked.connect(self.addItem)
        self.delBtn.clicked.connect(self.delItem)
        self.themeSwitcher.clicked.connect(self.themeSwitch)

        #Post Setup
        self.setCentralWidget(self.ui)
        self.loadBorrower()
        self.loadItem()
        ##theme
        theme = self.settings.value("UI/theme", "main")
        self.loadStyle(theme)

    def themeSwitch(self):
        if self.theme == "main":
            self.loadStyle("mainLight")
            self.settings.beginGroup("UI")
            self.settings.setValue("theme", "mainLight")
            self.settings.endGroup()
            self.settings.sync()
        elif self.theme == "mainLight":
            self.loadStyle("main")
            self.settings.beginGroup("UI")
            self.settings.setValue("theme", "main")
            self.settings.endGroup()
            self.settings.sync()

    def loadStyle(self, name:str):
        with open(self.resource_path(f"Ui/Style/{name}.qss"), "r") as f:
            self.setStyleSheet(f.read())
            self.theme = name
            if name == "main":
                self.themeSwitcher.setText("Light")
            else:
                self.themeSwitcher.setText("Dark")

    def addItem(self):
        accpt = False

        while(not accpt):
            name, ok = QInputDialog.getText(self, "Tambah Item", "Nama Item:")
            if name and ok:
                total, ok = QInputDialog.getInt(self, "Tambah Item", "Total Item:", minValue=1)
                if ok and total > 0:
                    self.db.addItem(name.lower(), total)
                    self.loadItem()
                    accpt = True
                    QMessageBox.information(self, "Sukses", f"Item '{name}' berhasil ditambahkan dengan total {total}.")
                elif ok and total <= 0:
                    QMessageBox.warning(self, "Input Error", "Total item harus lebih besar dari 0.")
                else:
                    accpt = True
            elif ok and not name:
                QMessageBox.warning(self, "Input Error", "Nama item tidak boleh kosong.")
            else:
                accpt = True

    def delItem(self):
        accpt = False
        while(not accpt):
            item,ok = QInputDialog.getItem(self, "Hapus Item", "Nama Item yang ingin dihapus:", self.itemsName) 
            if item and ok:
                amount, ok = QInputDialog.getInt(self, "Hapus Item", f"Jumlah item '{item}' yang ingin dihapus:", minValue=1, maxValue=int(self.itemTotals[item].text()))
                if ok and amount > 0:
                    self.db.delItem(item, amount)
                    self.loadItem()
                    accpt = True
            else:
                accpt = True

    def SearchBorrower(self, text):
        if(text == None):
            return
        
        for row in range(self.tableP.rowCount()):
            match = False
            item = self.tableP.item(row, 0)
            if item and text.lower() in item.text().lower():
                match = True

            self.tableP.setRowHidden(row, not match)

    def loadItem(self):
        items = self.db.getItem()
        self.itemsName = []
        self.tableI.setRowCount(len(items))
        self.tableI.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row, (name, total) in enumerate(items):
            item = QTableWidgetItem(name.capitalize())
            self.tableI.setItem(row, 0, item)
            self.itemsName.append(name)

            total = QTableWidgetItem(str(total))
            self.tableI.setItem(row, 1, total)
            self.itemTotals[name] = total

    def loadBorrower(self):
        borrowers = self.db.getBorrower()
        self.tableP.setRowCount(len(borrowers))
        self.tableP.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        for row, (name, key, tglP) in enumerate(borrowers):
            borrower = QTableWidgetItem(name)
            borrower.setData(Qt.UserRole, key)
            borrower.setData(Qt.UserRole + 1, name)
            self.tableP.setItem(row, 0, borrower)

            keyI = QTableWidgetItem(key)
            keyI.setData(Qt.UserRole, key)
            self.tableP.setItem(row, 1, keyI)

            tglPijam = QTableWidgetItem(tglP)
            tglPijam.setData(Qt.UserRole, key)
            self.tableP.setItem(row, 2, tglPijam)

    def selectBorrower(self, item):
        key = item.data(Qt.UserRole)
        dlg = itemBorrowedWindow(key, self.theme)
        dlg.exec()

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

class itemBorrowedWindow(QDialog):
    def __init__(self, key, theme):
        super().__init__()
        self.key = key
        self.theme = theme
        #Windows Setup
        self.setWindowTitle("Item Window[Admin]")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(self.resource_path("Assets/icon.png")))
        
        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/BorroweredItemAdmin.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage()

        #Reference
        self.table = self.ui.findChild(type(self.ui.BorroweredItem), "BorroweredItem")

        #Post Load
        self.loadBorrowItem()

        #UIs
        layouts = QVBoxLayout()
        layouts.addWidget(self.ui)
        self.setLayout(layouts)
        self.loadStyle()

    def loadStyle(self):
        with open(self.resource_path(f"Ui/Style/{self.theme}.qss"), "r") as f:
            self.setStyleSheet(f.read())

    def loadBorrowItem(self):
        items = self.db.getBorrowItem(self.key)
        self.table.setRowCount(len(items))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row, (_, itemName, tBorrow, dateP, _, dateK, tBack) in enumerate(items):
            item = QTableWidgetItem(str(itemName.capitalize()))
            self.table.setItem(row, 0, item)

            total = tBorrow - (tBack if tBack is not None else 0)

            if total > 0:
                status = QTableWidgetItem(f"Dipinjam {total}")
            else:
                status = QTableWidgetItem("Dikembalikan")
            self.table.setItem(row, 1, status)

            tanggalPinjam = QTableWidgetItem(dateP)
            self.table.setItem(row, 2, tanggalPinjam)
    
            if dateK is not None and tBack is not None:
                tanggalKembali = QTableWidgetItem(f"{dateK} kembali {tBack}")
            else:
                tanggalKembali = QTableWidgetItem("Belum dikembalikan")
            self.table.setItem(row, 3, tanggalKembali)

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main()
    window.show()
    sys.exit(app.exec())