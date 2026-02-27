import sqlite3,os,sys

class Storage():
    def __init__(self):
        super().__init__()
        self.conn = self.getDB()
        self.c = self.conn.cursor()
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS item (
            id TEXT PRIMARY KEY,
            total INTEGER
        )
        """)

        self.c.execute("""
        CREATE TABLE IF NOT EXISTS borrow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal_pinjam TEXT,
            nama_peminjam TEXT,
            key TEXT
        )
        """)

        self.c.execute("""
        CREATE TABLE IF NOT EXISTS borrowitem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peminjam_id INTEGER,
            nama_item TEXT,
            tanggal_pinjam TEXT,
            tanggal_kembali TEXT,
            amount INTEGER,
            FOREIGN KEY (peminjam_id) REFERENCES borrow(id)
        )
        """)

        self.conn.commit()
        self.conn.close()
        
    def is_frozen(self):
        return getattr(sys, "frozen", False)

    def getDB(self):
        if self.is_frozen():
            base = os.getenv("APPDATA")
            app_dir = os.path.join(base, "VLauncher")
        else:
            app_dir = "./Core/DB/"

        os.makedirs(app_dir, exist_ok=True)
        connDir = os.path.join(app_dir, "DataBase.db")
        conn = sqlite3.connect(connDir)
        return conn
    
    def addItem(self, name, total):
        self.conn = self.getDB()
        c = self.conn.cursor()
        c.execute("""
            INSERT INTO item (id, total)
            VALUES (?, ?)
            ON CONFLICT(id)
            DO UPDATE SET total = excluded.total
        """,(name, total))

        self.conn.commit()
        self.conn.close()
        print(f"Sukses menambah {name} dengan value {total}")

    def getItem(self):
        self.conn = self.getDB()
        self.c = self.conn.cursor()

        self.c.execute("""
            SELECT id, total FROM item
            ORDER BY id COLLATE NOCASE
        """)

        row = self.c.fetchall()
        self.conn.close()
        return row 
    
    def returnItem(self, items, date):
        conn = self.getDB()
        c = conn.cursor()

        for item, (amount, id) in items.items():
            c.execute("""
                UPDATE item SET total = total + ? WHERE id = ?
            """, (amount, item))

            c.execute("""
                UPDATE borrowitem SET amount = amount - ? WHERE id = ?
            """,(amount, id))

            c.execute("""
                UPDATE borrowitem SET tanggal_kembali = ? WHERE nama_item = ?
            """,(date, item))

        conn.commit()
        conn.close()

    # Borrow
    def borrowItem(self, items, key, date, peminjam):
        conn = self.getDB()
        c = conn.cursor()

        c.execute("""
            INSERT INTO borrow (tanggal_pinjam, nama_peminjam, key)
            VALUES (?, ?, ?)
        """,(date, peminjam, key))

        pid = c.lastrowid

        for item, amount in items.items():
            c.execute("""
                UPDATE item SET total = total - ? WHERE id = ?
            """, (amount, item))

            c.execute("""
                INSERT INTO borrowitem (peminjam_id, nama_item, tanggal_pinjam, amount)
                VALUES (?, ?, ?, ?)
            """, (pid, item, date, amount))

        conn.commit()
        conn.close()

    def getBorrowItem(self, key):
        conn = self.getDB()
        c = conn.cursor()

        c.execute("""
            SELECT borrow.key, borrowitem.nama_item, borrowitem.amount, borrowitem.tanggal_pinjam, borrowitem.id
            FROM borrow
            INNER JOIN borrowitem ON borrow.id = borrowitem.peminjam_id
            WHERE borrow.key = ?
        """, (key, ))

        rows = c.fetchall()
        c.close()
        conn.close()
        return rows
    
    def getBorrower(self):
        conn = self.getDB()
        c = conn.cursor()

        c.execute("""
            SELECT nama_peminjam, key, tanggal_pinjam FROM borrow
            ORDER BY nama_peminjam DESC
        """)

        rows = c.fetchall()
        c.close()
        conn.close()
        return rows