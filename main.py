import sys, os, string, random
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
QAbstractItemView, QMessageBox, QInputDialog, QDialog, QVBoxLayout, 
QSpinBox)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from Core import Storage
from datetime import datetime

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        #Windows Setup
        self.setWindowTitle("Aplikasi Inventaris")
        self.setGeometry(100, 100, 800, 600)
        
        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/main.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage.Storage()

        #Item Referencing
        self.table = self.ui.findChild(type(self.ui.ItemSelect), "ItemSelect")
        self.pjmbtn = self.ui.findChild(type(self.ui.PijamBtn), "PijamBtn")
        self.rtnW = self.ui.findChild(type(self.ui.RtnWindow), "RtnWindow")

        #button Setup
        self.pjmbtn.clicked.connect(self.getSelectedItem)
        self.rtnW.clicked.connect(self.BorrowerWindow)

        #Post Setup
        self.setCentralWidget(self.ui)
        #self.db.addItem("test", "5")
        self.loadItem()

    def rtnWindow(self):
        accpt = False

        while(accpt == False):
            text, ok = QInputDialog.getText(self, "Masukkan Kode", "Masukkan Kode Pijammu")
            if ok and text:
                items = self.db.getBorrowItem(text)
                if items:
                    accpt = True
                    dlg = returnWindow(items)
                    dlg.exec()
                elif not items:
                    QMessageBox.critical(self, "Error", "Kode Mu Tidak Ditemukan Di Database Kami")
            elif ok and not text:
                QMessageBox.critical(self, "Error", "Tolong Masukkan Kode Peminjaman")
            else:
                accpt = True

    def BorrowerWindow(self):
        dlg = borrowerWindow()
        dlg.exec()

    def loadItem(self):
        items = self.db.getItem()
        self.table.setRowCount(len(items))
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked
        )

        for row, (id, total) in enumerate(items):
            item = QTableWidgetItem(str(id))
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, item)

            _total = QTableWidgetItem(str(total))
            _total.setFlags(_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, _total)

            editable_item = QTableWidgetItem("0")
            editable_item.setFlags(editable_item.flags() | Qt.ItemFlag.ItemIsEditable)
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(total)
            self.table.setCellWidget(row, 1, spinbox)

    def getSelectedItem(self):
        date = datetime.now()
        formatDate =  date.strftime("%Y-%m-%d %H:%M")
        items = {}
        error = False

        text, ok = QInputDialog.getText(self, "Nama Peminjam", "Masukkan Nama Peminjam:")
        if ok and text:
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 0)
                if item != None and int(item.text()) > 0:
                    data = self.table.item(row, 2)
                    if data.checkState() == Qt.CheckState.Checked:
                        spinbox = self.table.cellWidget(row, 1)
                        amnt = spinbox.value()
                        if amnt > 0:
                            items[data.text()] = amnt
                        else:
                            error = True

            if len(items) > 0 and error == False:
                key = self.randomKeyCode()
                self.db.borrowItem(items, key, formatDate, text)
                self.loadItem()
                QMessageBox.information(self, "Kode Pijam", f"Kode Pijammu Adalah '{key}' SIMPAN DENGAN BAIK")
            elif error:
                QMessageBox.critical(self, "Error", "Tolong Masukkan Jumlah Item Yang Ingin Dipijam")
            else:
                QMessageBox.critical(self, "Error", "Tolong Memilih Setidaknya 1 Item")
        else:
            QMessageBox.critical(self, "Error", "Tolong Masukkan Nama Peminjam")

    def randomKeyCode(self):
        chars = string.ascii_uppercase + string.digits
        key = "".join([random.choice(chars) for _ in range(4)])

        print(key)
        return key

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

class borrowerWindow(QDialog):
    def __init__(self):
        super().__init__()
        #Windows Setup
        self.setWindowTitle("Peminjam Barang")
        self.setGeometry(100, 100, 500, 400)
        
        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/borrower.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage.Storage()

        #Item Referencing
        self.table = self.ui.findChild(type(self.ui.ItemSelect), "ItemSelect")
        self.borrowLabel = self.ui.findChild(type(self.ui.borrowLabel), "borrowLabel")

        #Load Thing
        self.loadBorrower()
        self.table.itemClicked.connect(self.selectBorrower)

        #Post Load
        layouts = QVBoxLayout()
        layouts.addWidget(self.ui)
        self.setLayout(layouts)

    def loadBorrower(self):
        borrowers = self.db.getBorrower()
        self.table.setRowCount(len(borrowers))
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        for row, (name, key) in enumerate(borrowers):
            borrower = QTableWidgetItem(name)
            borrower.setData(Qt.UserRole, key)
            borrower.setData(Qt.UserRole + 1, name)
            self.table.setItem(row, 0, borrower)

    def selectBorrower(self, item):
        key = item.data(Qt.UserRole)
        items = self.db.getBorrowItem(key)
        dlg = returnWindow(items)
        dlg.exec()

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

class returnWindow(QDialog):
    def __init__(self, items):
        super().__init__()
        self.items = items
        #Windows Setup
        self.setWindowTitle("Kembalikan Barang")
        self.setGeometry(100, 100, 500, 400)
        
        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/return.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage.Storage()

        #Item Referencing
        self.table = self.ui.findChild(type(self.ui.ItemSelect), "ItemSelect")
        self.RtnBtn = self.ui.findChild(type(self.ui.ReturnBtn), "ReturnBtn")
        self.borrowLabel = self.ui.findChild(type(self.ui.borrowLabel), "borrowLabel")

        #Load Thing
        self.loadBorrowItem()
        self.RtnBtn.clicked.connect(self.returnSelectedItem)

        #Post Load
        layouts = QVBoxLayout()
        layouts.addWidget(self.ui)
        self.setLayout(layouts)

    def loadBorrowItem(self):
        items = self.items
        self.table.setRowCount(len(items))
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked |
            QAbstractItemView.EditTrigger.SelectedClicked
        )

        for row, (_, itemName, total, date, id) in enumerate(items):
            item = QTableWidgetItem(str(itemName))
            item.setData(Qt.UserRole, id)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, item)

            _total = QTableWidgetItem(str(total))
            _total.setFlags(_total.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, _total)

            editable_item = QTableWidgetItem("0")
            editable_item.setFlags(editable_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, editable_item)
            spinbox = QSpinBox()
            spinbox.setMinimum(0)
            spinbox.setMaximum(total)
            self.table.setCellWidget(row, 1, spinbox)
            _date = date

        self.borrowLabel.setText(f"Pilih Item Yang Anda Pijam Pada {_date} Dan Ingin Dikembalikan")

    def returnSelectedItem(self):
        date = datetime.now()
        formatDate =  date.strftime("%Y-%m-%d %H:%M")
        items = {}
        error = False

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item != None and int(item.text()) > 0:
                data = self.table.item(row, 2)
                if data.checkState() == Qt.CheckState.Checked:
                    amnt = self.table.cellWidget(row, 1).value()
                    id = data.data(Qt.UserRole)
                    if amnt > 0:
                        itemdata = (amnt, id)
                        items[data.text()] = itemdata
                    else:
                        error = True

        if len(items) > 0 and error == False:
            self.db.returnItem(items, formatDate)
            QMessageBox.information(self, "Terimakasih", "Terimakasih Telah Mengembalikan")
        elif error:
            QMessageBox.critical(self, "Error", "Tolong Masukkan Jumlah Item Yang Ingin Dipijam")
        else:
            QMessageBox.critical(self, "Error", "Tolong Memilih Setidaknya 1 Item")

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main()
    window.show()
    sys.exit(app.exec())