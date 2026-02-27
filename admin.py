from Core.Storage import Storage
from PySide6.QtWidgets import (QMainWindow, QApplication, QAbstractItemView, QSpinBox,
QTableWidgetItem, QDialog, QVBoxLayout, QInputDialog, QMessageBox)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
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

        #Reference
        self.tableP = self.ui.findChild(type(self.ui.PeminjamTable), "PeminjamTable")
        self.searchBarP = self.ui.findChild(type(self.ui.CariPeminjam), "CariPeminjam")
        self.tableI = self.ui.findChild(type(self.ui.ItemTable), "ItemTable")
        self.addBtn = self.ui.findChild(type(self.ui.TambahItemBtn), "TambahItemBtn")
        self.delBtn = self.ui.findChild(type(self.ui.HapusItemBtn), "HapusItemBtn")

        #Connect Thing
        self.searchBarP.textChanged.connect(self.SearchBorrower)
        self.tableP.itemClicked.connect(self.selectBorrower)
        self.addBtn.clicked.connect(self.addItem)
        self.delBtn.clicked.connect(self.delItem)

        #Post Setup
        self.setCentralWidget(self.ui)
        self.loadBorrower()
        self.loadItem()

    def addItem(self):
        accpt = False

        while(not accpt):
            name, ok = QInputDialog.getText(self, "Tambah Item", "Nama Item:")
            if name and ok:
                total, ok = QInputDialog.getInt(self, "Tambah Item", "Total Item:", minValue=0)
                if ok and total > 0:
                    self.db.addItem(name, total)
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
                self.db.delItem(item)
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
            item = QTableWidgetItem(name)
            self.tableI.setItem(row, 0, item)
            self.itemsName.append(name)

            total = QTableWidgetItem(str(total))
            self.tableI.setItem(row, 1, total)

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
        dlg = itemBorrowedWindow(key)
        dlg.exec()

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

class itemBorrowedWindow(QDialog):
    def __init__(self, key):
        super().__init__()
        self.key = key
        #Windows Setup
        self.setWindowTitle("Item Window[Admin]")
        self.setGeometry(100, 100, 800, 600)
        
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

    def loadBorrowItem(self):
        items = self.db.getBorrowItem(self.key)
        self.table.setRowCount(len(items))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row, (_, itemName, tBorrow, dateP, _, dateK, tBack) in enumerate(items):
            item = QTableWidgetItem(str(itemName))
            self.table.setItem(row, 0, item)

            total = tBorrow - (tBack if tBack is not None else 0)

            if total > 0:
                status = QTableWidgetItem(f"Dipinjam {total}")
            else:
                status = QTableWidgetItem("Dikembalikan")
            self.table.setItem(row, 1, status)

            tanggalPinjam = QTableWidgetItem(dateP)
            self.table.setItem(row, 2, tanggalPinjam)
    
            tanggalKembali = QTableWidgetItem(f"{dateK} kembali {tBack}")
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