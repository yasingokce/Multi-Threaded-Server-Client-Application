import threading
import socket
import mysql.connector
from mysql.connector import Error
import os
import hlib
import clientslist
import personel
import messageslist
import dotenv

dotenv.load_dotenv()
fn = os.path.basename(__file__)


# MySQL connection function
def create_mysql_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=os.getenv("MYSQL_PORT"),
            database=os.getenv("MYSQL_DBNAME"),
            user=os.getenv("MYSQL_USERNAME"),
            password=os.getenv("MYSQL_PASSWORD")
        )
        if connection.is_connected():
            hlib.logs(fn, "MySQL connection successful")

        return connection
    except Error as e:
        hlib.logs(fn, f"MySQL connection error: {e}")
        return None


# Server Class
class Server:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.clients = {}  # Connected clients: {client_id: (client_socket, addr, local_port)}
        self.connection = create_mysql_connection()
        clientslist.init_db(self)
        personel.init_db(self)
        messageslist.init_db(self)
        self.noone = False

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        hlib.logs(fn, f"Server {self.host}:{self.port} It works at the address")
        print(f"Server {self.host}:{self.port} It works at the address")

        # Start a thread for the command interface
        command_thread = threading.Thread(target=self.command_interface)
        command_thread.start()

        while True:
            client_socket, addr = server_socket.accept()
            hlib.logs(fn, f"Connection received from  {addr} .")
            client_handler = threading.Thread(
                target=self.handle_client,
                args=(client_socket, addr)
            )
            client_handler.start()

    def handle_client(self, client_socket, addr):
        client_id = None
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                hlib.logs(fn, f"Message from client: {message}")

                # Client registration process
                if message.startswith("REGISTER_CLIENT"):
                    parts = message.split(',')
                    client_id = int(parts[1])
                    local_port = int(parts[2])

                    # Register client
                    self.clients[client_id] = (client_socket, addr, local_port)
                    with self.lock:
                        cursor = self.connection.cursor()
                        # Check if there is a record in the database that matches the id
                        check_query = "SELECT id FROM clients WHERE id = %s"
                        cursor.execute(check_query, (client_id,))
                        result = cursor.fetchone()
                        if result:
                            hlib.logs(fn, f"id {client_id} already exists. No data added.")
                        else:
                            # If record does not exist, insert data
                            insert_query = """INSERT INTO clients (id, name, host, port) 
                                                                  VALUES (%s, %s, %s, %s)"""
                            record = (client_id, f"Client_{client_id}", addr[0], local_port)
                            cursor.execute(insert_query, record)
                            self.connection.commit()
                    hlib.logs(fn, f"Client {client_id} saved.")
                elif message.startswith("No"):
                    self.noone = True
                else:
                    self.process_message(message, client_socket, client_id)
            except Exception as e:
                hlib.logs(fn, f"Error: {e}")
                client_socket.close()
                if client_id in self.clients:
                    del self.clients[client_id]
                break

    def print_client_list(self):
        print("Current Client List:")
        for cid, (sock, address, port) in self.clients.items():
            print(f"ID: {cid}, Adres: {address}, Port: {port}")

    # 1. Send a specific personnel to a specific client.
    def send_personnel_to_client(self, personnel_id, client_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, surname, ssn FROM personnel WHERE id = %s", (personnel_id,))
        personnel = cursor.fetchone()
        if personnel and client_id in self.clients:
            message = f"SAVE_PERSONNEL,{personnel[0]},{personnel[1]},{personnel[2]}"
            client_socket, _, _ = self.clients[client_id]
            client_socket.send(message.encode('utf-8'))
            if self.noone:
                print(f"{personnel_id} Personnel is available on the client")
                self.noone = False
            else:
                print(f"Personnel {personnel_id} send to Client {client_id}.")
        else:
            print(f"No Personnel or Clients found.")

    # 2. Send a specific personnel to all clients.
    def send_personnel_to_all_clients(self, personnel_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, surname, ssn FROM personnel WHERE id = %s", (personnel_id,))
        personnel = cursor.fetchone()
        if personnel:
            message = f"SAVE_PERSONNEL,{personnel[0]},{personnel[1]},{personnel[2]}"
            self.send_message_to_all_clients(message)
            print(f"Personnel {personnel_id} sent to all Clients.")
        else:
            print("No Personnel found.")

    # 3. Send all personnel to all clients.
    def send_all_personnel_to_all_clients(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT name, surname, ssn FROM personnel")
        personnel_list = cursor.fetchall()
        for personnel in personnel_list:
            message = f"SAVE_PERSONNEL,{personnel[0]},{personnel[1]},{personnel[2]}"
            self.send_message_to_all_clients(message)
        print("All Personnel sent to all Clients.")

    # 4. Delete a specific personnel from a specific client.
    def delete_personnel_from_client(self, personnel_id, client_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT ssn FROM personnel WHERE id = %s", (personnel_id,))
        ssn = cursor.fetchone()
        if ssn and client_id in self.clients:
            message = f"DELETE_PERSONNEL,{ssn[0]}"
            client_socket, _, _ = self.clients[client_id]
            client_socket.send(message.encode('utf-8'))
            print(f"Personnel {personnel_id} deleted from Client {client_id}.")
        else:
            print(f"No Personnel or Clients found.")

    # 5. Delete a specific personnel from all clients.
    def delete_personnel_from_all_clients(self, personnel_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT ssn FROM personnel WHERE id = %s", (personnel_id,))
        ssn = cursor.fetchone()
        if ssn:
            message = f"DELETE_PERSONNEL,{ssn[0]}"
            self.send_message_to_all_clients(message)
            print(f"Personnel {personnel_id} deleted from all clients.")
        else:
            print("Personnel not found.")

    # 6. Delete all personnel from all clients.
    def delete_all_personnel_from_all_clients(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT ssn FROM personnel")
        personnel_list = cursor.fetchall()
        for personnel in personnel_list:
            message = f"DELETE_PERSONNEL,{personnel[0]}"
            self.send_message_to_all_clients(message)
        print("All Personnel deleted from all Clients.")

    # Helper: Send message to all clients
    def send_message_to_all_clients(self, message):
        for client_id, (client_socket, _, _) in self.clients.items():
            try:
                client_socket.send(message.encode('utf-8'))
                print(f"Message send to Client {client_id}.")
            except Exception as e:
                print(f"Failed to send message to Client {client_id}: {e}")

    def command_interface(self):
        # Command Interface
        print(
            "# 1. Send a specific personnel to a specific client. = 'send <Personnel-Id> <Client-Id>'"
            "\n# 2. Send a specific personnel to all clients. = 'send all <Personnel-Id>'"
            "\n# 3. Send all personnel to all clients. = 'apac'"
            "\n# 4. Delete a specific personnel from a specific client.= 'delete <Personnel-Id> <Client-Id>'"
            "\n# 5. Delete a specific personnel from all clients.= 'delete all <Personnel-Id>'"
            "\n# 6. Delete all personnel from all clients.=  'dapac'"
            "\n7.List Clients.= 'list_clients'"
            "\n8.Exit")
        print("Command System Started! You can enter your commands.")
        while True:
            command = input("> ").strip()

            if command.startswith("send"):
                parts = command.split()
                if len(parts) == 3:
                    client_id = int(parts[1])
                    personnel_id = int(parts[2])
                    self.send_personnel_to_client(client_id, personnel_id)
                # All Clients
                elif len(parts) == 2 and parts[1] == "all":
                    personnel_id = int(parts[2])
                    self.send_personnel_to_all_clients(personnel_id)
                else:
                    print("Wrong command format! Correct format: send <client_id> <personnel_id>")

            elif command.startswith("delete"):
                parts = command.split()
                if len(parts) == 3:
                    client_id = int(parts[1])
                    personnel_id = int(parts[2])
                    self.delete_personnel_from_client(client_id, personnel_id)
                # All Clients
                elif len(parts) == 2 and parts[1] == "all":
                    personnel_id = int(parts[2])
                    self.delete_personnel_from_all_clients(personnel_id)
                else:
                    print("Wrong command format! Correct format: delete <client_id> <personnel_id>")

            elif command == "apac":
                self.send_all_personnel_to_all_clients()

            elif command == "dapac":
                self.delete_all_personnel_from_all_clients()

            elif command == "list_clients":
                self.print_client_list()

            elif command == "exit":
                print("Server is shutting down...")
                exit(0)

            else:
                print("Unknown command! Valid commands: send, delete, apac, dapac, list_clients, exit")
