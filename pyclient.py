import socket
import sqlite3
import threading
import hlib
import os

fn = os.path.basename(__file__)


# SQLite connection function
def create_sqlite_connection(client_id):
    db_name = f'client_{client_id}_database.db'
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS personnel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        surname TEXT,
        ssn TEXT
    )
    ''')
    connection.commit()
    return connection


# Client Class
class Client:
    def __init__(self, client_id, local_port, server_host='localhost', server_port=12345):
        self.client_id = client_id
        self.local_port = local_port
        self.server_host = server_host
        self.server_port = server_port
        self.connection = create_sqlite_connection(client_id)
        self.client_socket = None

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to a specific port number
        self.client_socket.bind(('', self.local_port))
        self.client_socket.connect((self.server_host, self.server_port))
        hlib.logs(fn, f"The Client {self.client_id} connected to the server as .")
        # We send our own port number to the server
        register_message = f"REGISTER_CLIENT,{self.client_id},{self.local_port}"
        self.client_socket.send(register_message.encode('utf-8'))

    def listen_for_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                hlib.logs(fn, f"Message from server (Client {self.client_id}): {message}")
                self.handle_message(message)
            except Exception as e:
                hlib.logs(fn, f"Connection error (Client {self.client_id}): {e}")
                self.client_socket.close()
                break

    # Processing the message (saving and deleting operations)
    def handle_message(self, message):
        cursor = self.connection.cursor()
        parts = message.split(',')
        command = parts[0]

        if command == "SAVE_PERSONNEL":
            # Format of the message: SAVE_PERSONNEL,name,surname,ssn
            name = parts[1]
            surname = parts[2]
            ssn = parts[3]
            # check
            check_query = "SELECT ssn FROM personnel WHERE ssn = ?"
            cursor.execute(check_query, (ssn,))
            result = cursor.fetchone()

            if result:
                hlib.logs(fn, f"ssn {ssn} already exists. No data added.")
                self.client_socket.send((f"No data added. ssn {ssn} already exists.").encode('utf-8'))
            else:
                insert_query = '''
                INSERT INTO personnel (name, surname, ssn)
                VALUES (?, ?, ?)
                '''
                record = (name, surname, ssn)
                cursor.execute(insert_query, record)
                self.connection.commit()
                hlib.logs(fn, f"{name} {surname} ({ssn}) recorded. (Client {self.client_id})")

        elif command == "DELETE_PERSONNEL":
            # Format of the message: DELETE_PERSONNEL,ssn
            ssn = parts[1]
            cursor.execute('DELETE FROM personnel WHERE ssn = ?', (ssn,))
            self.connection.commit()
            hlib.logs(fn, f"{ssn} Numbered personnel deleted. (Client {self.client_id})")


# Running the client
def run_client(client_id, local_port):
    client = Client(client_id, local_port)
    client.connect_to_server()
    client.listen_for_messages()


# We use threading to create multiple clients
if __name__ == "__main__":
    num_clients = 3  # Ex. 3 Clients
    client_threads = []
    starting_port = 5001  # The value at which client port numbers will start

    for i in range(num_clients):
        client_id = i + 1
        local_port = starting_port + i  # A different port for each client
        client_thread = threading.Thread(target=run_client, args=(client_id, local_port))
        hlib.logs(fn, f"{local_port} connected from port")
        client_threads.append(client_thread)
        client_thread.start()

    for thread in client_threads:
        thread.join()
