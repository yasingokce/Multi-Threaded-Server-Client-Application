import hlib
import os
fn = os.path.basename(__file__)
def init_db(self):
    cursor = self.connection.cursor()
    # create  client table
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS personnel (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(40),
                    surname VARCHAR(40),
                    ssn VARCHAR(20)
                )
            ''')

    def insert_client_if_not_exists(id, name, surname, ssn):
        # Check if there is a record in the database that matches ssn
        check_query = "SELECT ssn FROM personnel WHERE ssn = %s"
        cursor.execute(check_query, (ssn,))
        result = cursor.fetchone()

        if result:
            hlib.logs(fn,f"ssn {ssn} already exists. No data added.")
        else:
            # If record does not exist, insert data
            insert_query = """INSERT INTO personnel (id, name, surname, ssn) 
                                      VALUES (%s, %s, %s, %s)"""
            record = (id, name, surname, ssn)
            cursor.execute(insert_query, record)
            self.connection.commit()
            hlib.logs(fn,f"ssn {ssn} was successfully added")

    # read and write this part from file !!!!
    insert_client_if_not_exists(1, 'Isaac', 'Newton', 12345678900)
    insert_client_if_not_exists(2, 'Albert', 'Einstein', 98765432100)
    insert_client_if_not_exists(3, 'Yasin', 'Gokce', 145878562)
    insert_client_if_not_exists(4, 'Mehmet', 'Sahin', 547985627)


