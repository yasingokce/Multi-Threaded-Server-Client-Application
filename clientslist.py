def init_db(self):
    with self.lock:
        cursor = self.connection.cursor()
        # create  client table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INT PRIMARY KEY,
                name VARCHAR(20),
                host VARCHAR(20),
                port INT
            )
        ''')
        #Clear client list every time.
        cursor.execute('''
                       DELETE  FROM clients 
                   ''')
        self.connection.commit()
