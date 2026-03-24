import sqlite3
from Core.Storage import Storage

def test_add_item():
    conn = sqlite3.connect(":memory:")
    storage = Storage(test_conn=conn)

    storage.addItem("Test1", 5)
    storage.addItem("Test1", 3)

    result = storage.getItem()
    assert result == [("Test1", 8)]

def test_remove_item():
    conn = sqlite3.connect(":memory:")
    storage = Storage(test_conn=conn)

    storage.addItem("Test2", 10)
    storage.delItem("Test2", 4)

    result = storage.getItem()
    assert result == [("Test2", 6)]

def test_getborrowerbykey():
    conn = sqlite3.connect(":memory:")
    storage = Storage(test_conn=conn)

    storage.borrowItem({"Test3": 3}, "QWERTY", "02-01-2026", "Vrw")
    storage.borrowItem({"Test2": 2, "Test4": 3}, "ASDF", "02-02-2026", "Vrw2")

    borrowers = storage.getBorrowerByKey(["QWERTY", "ASDF"])

    for row, (borrower, _, _) in enumerate(borrowers):
        assert borrowers[row][0] == borrower

def test_borrowitem():
    conn = sqlite3.connect(":memory:")
    storage = Storage(test_conn=conn)

    storage.borrowItem({"Test3": 3}, "QWERTY", "02-01-2026", "Vrw")
    
    Borrowers = storage.getBorrower()

    assert len(Borrowers) == 1

    nama, key, _ = Borrowers[0]
    assert nama == "Vrw"

    items = storage.getBorrowItem(key)

    assert len(items) == 1

    _, nama_item, amount, *_ = items[0]
    assert nama_item == "Test3"
    assert amount == 3

def test_returnItem():
    conn = sqlite3.connect(":memory:")
    storage = Storage(test_conn=conn)

    storage.borrowItem({"Test4": 1}, "ASDF", "2026-02-01", "Vrw2")
    storage.returnItem({"Test4":(1,1)}, "2026-02-02")

    Borrowers = storage.getBorrower()

    assert len(Borrowers) == 1

    nama, key, _ = Borrowers[0]
    assert nama == "Vrw2"

    items = storage.getBorrowItem(key)

    assert len(items) == 1

    _, itemName, tBorrow, dateP, _, dateK, tBack = items[0]
    assert itemName == "Test4"
    assert tBorrow == 1
    assert dateP == "2026-02-01"
    assert dateK == "2026-02-02"
    assert tBack == 1
