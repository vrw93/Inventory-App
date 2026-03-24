import sqlite3, os, sys

class Storage():
    def __init__(self, test_conn=None):
        self._test_conn = test_conn
        self._init_db()

    def _init_db(self):
        with self.getDB() as conn:
            c = conn.cursor()

            c.execute("""
            CREATE TABLE IF NOT EXISTS item (
                id TEXT PRIMARY KEY,
                total INTEGER NOT NULL CHECK(total >= 0)
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS borrow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal_pinjam TEXT,
                nama_peminjam TEXT,
                key TEXT
            )
            """)

            c.execute("""
            CREATE TABLE IF NOT EXISTS borrowitem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peminjam_id INTEGER,
                nama_item TEXT,
                tanggal_pinjam TEXT,
                tanggal_kembali TEXT,
                amount INTEGER,
                amount_back INTEGER,
                FOREIGN KEY (peminjam_id) REFERENCES borrow(id)
            )
            """)

    def is_frozen(self):
        return getattr(sys, "frozen", False)

    def getDB(self):
        if self._test_conn:
            return self._test_conn

        if self.is_frozen():
            base = os.getenv("APPDATA") or os.path.expanduser("~/.config")
            app_dir = os.path.join(base, "VLauncher")
        else:
            app_dir = "./Core/DB/"

        os.makedirs(app_dir, exist_ok=True)
        connDir = os.path.join(app_dir, "DataBase.db")
        return sqlite3.connect(connDir)

    #Item
    def addItem(self, name, total):
        with self.getDB() as conn:
            conn.execute("""
                INSERT INTO item (id, total)
                VALUES (?, ?)
                ON CONFLICT(id)
                DO UPDATE SET total = total + excluded.total
            """, (name, total))

    def delItem(self, name, amount: int):
        with self.getDB() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            c = conn.cursor()

            try:
                c.execute("""
                    UPDATE item SET total = total - ?
                    WHERE id = ? AND total > ?
                """, (amount, name, amount))

                if c.rowcount == 0:
                    c.execute("""
                        DELETE FROM item WHERE id = ? AND total <= ?
                    """, (name, amount))
            except Exception:
                conn.rollback()
                raise

    def getItem(self):
        with self.getDB() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, total FROM item
                ORDER BY id COLLATE NOCASE
            """)
            return c.fetchall()

    #borrow
    def borrowItem(self, items, key, date, peminjam):
        with self.getDB() as conn:
            c = conn.cursor()

            c.execute("""
                INSERT INTO borrow (tanggal_pinjam, nama_peminjam, key)
                VALUES (?, ?, ?)
            """, (date, peminjam, key))

            pid = c.lastrowid

            for item, amount in items.items():
                c.execute("""
                    UPDATE item SET total = total - ? WHERE id = ?
                """, (amount, item))

                c.execute("""
                    INSERT INTO borrowitem (peminjam_id, nama_item, tanggal_pinjam, amount)
                    VALUES (?, ?, ?, ?)
                """, (pid, item, date, amount))

    def returnItem(self, items, date):
        with self.getDB() as conn:
            c = conn.cursor()

            for item, (amount, id) in items.items():
                c.execute("""
                    UPDATE item SET total = total + ? WHERE id = ?
                """, (amount, item))

                c.execute("""
                    UPDATE borrowitem SET amount_back = ? WHERE id = ?
                """, (amount, id))

                c.execute("""
                    UPDATE borrowitem SET tanggal_kembali = ? WHERE nama_item = ?
                """, (date, item))

    def getBorrowItem(self, key:str):
        with self.getDB() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT borrow.key, borrowitem.nama_item, borrowitem.amount, 
                borrowitem.tanggal_pinjam, borrowitem.id, 
                borrowitem.tanggal_kembali, borrowitem.amount_back
                FROM borrow
                INNER JOIN borrowitem ON borrow.id = borrowitem.peminjam_id
                WHERE borrow.key = ?
            """, (key,))
            return c.fetchall()

    def getBorrower(self):
        with self.getDB() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT nama_peminjam, key, tanggal_pinjam FROM borrow
                ORDER BY nama_peminjam DESC
            """)
            return c.fetchall()
        
    def getBorrowerByKey(self, keys: list):
        with self.getDB() as conn:
            c = conn.cursor()
            placeholders = ','.join('?' * len(keys))
            c.execute(f"""
                SELECT nama_peminjam, key, tanggal_pinjam FROM borrow
                WHERE borrow.key IN ({placeholders})
            """, keys)
            return c.fetchall()