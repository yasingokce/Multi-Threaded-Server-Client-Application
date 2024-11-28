import os
import hlib
fn = os.path.basename(__file__)
def init_db(self):
    cursor = self.connection.cursor()
    # create client table
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    clientid INT,
                    payload TEXT,
                    FOREIGN KEY (clientid) REFERENCES clients(id)
                )
            ''')

    def insert_client_if_not_exists(id, clientid, payload):
        # Check if there is a record in the database that matches ssn
        check_query = "SELECT id FROM messages WHERE id = %s"
        cursor.execute(check_query, (id,))
        result = cursor.fetchone()

        if result:
            hlib.logs(fn, f"ID {id} the message in already exists. No data was added.")
        else:
            # If record does not exist, insert data
            insert_query = """INSERT INTO messages (id, clientid, payload) 
                                      VALUES (%s, %s, %s)"""
            record = (id, clientid, payload)
            cursor.execute(insert_query, record)
            self.connection.commit()
            hlib.logs(fn,"message inserted.")

    # Insert data
    insert_client_if_not_exists(1, '1', 'mesagges')
    insert_client_if_not_exists(2, '2', 'mesagges for personnels')
    insert_client_if_not_exists(3, '2', 'mesagges')
    insert_client_if_not_exists(4, '4', 'mesagges for personnels')




