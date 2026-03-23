from Core.Storage import Storage
from PySide6.QtWidgets import (QMainWindow, QApplication, QAbstractItemView, QFileDialog,
QTableWidgetItem, QDialog, QVBoxLayout, QInputDialog, QMessageBox, QTableWidget, QPushButton,
QLineEdit)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QSettings
from PySide6.QtGui import QIcon
import sys, os
import pandas as pd
from datetime import datetime
from collections import defaultdict

class main(QMainWindow):
    def __init__(self):
        super().__init__()
        #Variable
        self.itemTotals = {}
        self.maxRecent = 10

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
        self.tableP:QTableWidget = self.ui.findChild(type(self.ui.PeminjamTable), "PeminjamTable")
        self.searchBarP:QLineEdit = self.ui.findChild(type(self.ui.CariPeminjam), "CariPeminjam")
        self.tableI:QTableWidget = self.ui.findChild(type(self.ui.ItemTable), "ItemTable")
        self.addBtn:QPushButton = self.ui.findChild(type(self.ui.TambahItemBtn), "TambahItemBtn")
        self.delBtn:QPushButton = self.ui.findChild(type(self.ui.HapusItemBtn), "HapusItemBtn")
        self.themeSwitcher:QPushButton = self.ui.findChild(type(self.ui.ThemeSwitcher), "ThemeSwitcher")
        self.exportcsvbtn:QPushButton = self.ui.findChild(type(self.ui.ExportCSVBtn), "ExportCSVBtn")
        self.recentBorrowerOvrvw:QTableWidget = self.ui.findChild(type(self.ui.CurrentBorrowerTab), "CurrentBorrowerTab")
        self.recentItemOvrvw:QTableWidget = self.ui.findChild(type(self.ui.CurrentItemTab), "CurrentItemTab")

        #Connect Thing
        self.searchBarP.textChanged.connect(self.SearchBorrower)
        self.tableP.itemClicked.connect(self.selectBorrower)
        self.recentBorrowerOvrvw.itemClicked.connect(self.selectBorrower)
        self.addBtn.clicked.connect(self.addItem)
        self.delBtn.clicked.connect(self.delItem)
        self.themeSwitcher.clicked.connect(self.themeSwitch)
        self.exportcsvbtn.clicked.connect(self.csvExport)
        self.recentItemOvrvw.itemClicked.connect(self.selectBorrowerByItem)

        #Post Setup
        self.setCentralWidget(self.ui)
        self.loadBorrower()
        self.loadItem()
        self.recentUser()
        self.recentItem()

        #theme
        theme = self.settings.value("UI/theme", "main")
        self.loadStyle(theme)

    def selectBorrowerByItem(self, item):
        key = item.data(Qt.UserRole)
        dlg = BorrowerWindow(key, self.theme)
        dlg.exec()

    def recentItem(self):
        userdata = self.db.getBorrower()
        items = []
        keys = [row[1] for row in userdata]

        #Collect All Borrowed Items
        for key in keys:
            datas = self.db.getBorrowItem(key)
            items.extend([(row[0], row[1], row[2], row[3], row[6]) for row in datas])

        #Remove Unnecessary Data
        grouped = defaultdict(lambda: {"count": 0, "date": "", "keys": []})
        for key, name, count, date, countb in items:
            grouped[name]["count"] += (count - countb if countb is not None else count)
            grouped[name]["keys"].append(key)
            if date > grouped[name]["date"]:
                grouped[name]["date"] = date

        #Sorting Into Recent Item
        item = [(name, val["count"], val["date"], val["keys"]) for name, val in grouped.items()]
        itemSorted = sorted(item, key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M'), reverse=True)

        self.recentItemOvrvw.setRowCount(min(len(itemSorted), self.maxRecent))

        indx = 0
        for row, (_name, _count, _, _keys) in enumerate(itemSorted):
            indx += 1
            if indx < self.maxRecent:
                name = QTableWidgetItem(_name)
                name.setData(Qt.UserRole, _keys)
                self.recentItemOvrvw.setItem(row, 0, name)

                counts = QTableWidgetItem(str(_count))
                counts.setData(Qt.UserRole, _keys)
                self.recentItemOvrvw.setItem(row, 1, counts)

    def recentUser(self):
        datas = self.db.getBorrower()
        datasSorted = sorted(datas, key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M'), reverse=True)

        self.recentBorrowerOvrvw.setRowCount(min(len(datasSorted), self.maxRecent))

        def getBorrowedCount(obj, key):
            data = obj.db.getBorrowItem(key)
            filteredData = [row[2] for row in data]
            return sum(filteredData)

        indx = 0
        for row, (_name, _key, _) in enumerate(datasSorted):
            indx += 1
            if indx < self.maxRecent:
                name = QTableWidgetItem(_name)
                name.setData(Qt.UserRole, _key)
                self.recentBorrowerOvrvw.setItem(row, 0, name)

                borrowedCount = getBorrowedCount(self, _key)
                count = QTableWidgetItem(str(borrowedCount))
                count.setData(Qt.UserRole, _key)
                self.recentBorrowerOvrvw.setItem(row, 1, count)

    def csvExport(self):
        borrower = self.db.getBorrower()
        data = {}

        for (peminjam, key, tglP) in borrower:
            items = self.db.getBorrowItem(key)
            data[peminjam] = (tglP, items)

        rows = []
        for key, (date, items) in data.items():
            for item in items:
                rows.append([key, date] + list(item))

        columns = ['Borrower', 'Borrower Date', 'Key', 'Item', 'Amount', 'Borrow Date', 'Item Id', 'Return Date', 'Return Amount']
        df = pd.DataFrame(rows, columns=columns)

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "CSV file (*.csv);;Text File (*.txt);;All File (*.*)"
        )
        if filename:
            df.to_csv(filename, index=False, sep=';')

            QMessageBox.information(self, "CSV Export", "Succesfully Export CSV")

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
        self.table:QTableWidget = self.ui.findChild(type(self.ui.BorroweredItem), "BorroweredItem")

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

class BorrowerWindow(QDialog):
    def __init__(self, key:list, theme):
        super().__init__()
        self.key = key
        self.theme = theme
        #Windows Setup
        self.setWindowTitle("Borrower Window[Admin]")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(self.resource_path("Assets/icon.png")))
        
        #File/DB
        loader = QUiLoader()
        file = QFile(self.resource_path("Ui/borrower.ui"))
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.db = Storage()

        #Ref
        self.table:QTableWidget = self.ui.findChild(type(self.ui.ItemSelect), "ItemSelect")

        #Connection
        self.table.itemClicked.connect(self.selectBorrower)

        #postLoad
        self.loadBorrower()

        #UIs
        layouts = QVBoxLayout()
        layouts.addWidget(self.ui)
        self.setLayout(layouts)
        self.loadStyle()

    def selectBorrower(self, item):
        key = item.data(Qt.UserRole)
        dlg = itemBorrowedWindow(key, self.theme)
        dlg.exec()

    def loadBorrower(self):
        data = self.db.getBorrowerByKey(self.key)

        self.table.setRowCount(len(data))
        
        for row, (_name, _key, _date) in enumerate(data):
            name = QTableWidgetItem(_name)
            name.setData(Qt.UserRole, _key)
            self.table.setItem(row, 0, name)

            key = QTableWidgetItem(_key)
            key.setData(Qt.UserRole, _key)
            self.table.setItem(row, 1, key)

            date = QTableWidgetItem(_date)
            date.setData(Qt.UserRole, _key)
            self.table.setItem(row, 2, date)

    def loadStyle(self):
        with open(self.resource_path(f"Ui/Style/{self.theme}.qss"), "r") as f:
            self.setStyleSheet(f.read())

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main()
    window.show()
    sys.exit(app.exec())