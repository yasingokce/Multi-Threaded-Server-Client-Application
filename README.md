# **Multi-Threaded Server-Client Python Application**

This project implements a multi-threaded server-client architecture where the server manages client and personnel data using MySQL, and clients store their data in SQLite. The server communicates with multiple clients, performing various operations based on commands, while clients process and store the received data.

---

## **Features**

- Server-side management of client and personnel data using **MySQL**.
- Local storage of personnel records on clients using **SQLite**.
- Multi-client support with unique operations for each client.
- Command-based interface (CLI) for managing server operations.
- Operations to send or delete data for specific clients or all clients.

---

## **Setup**

### Requirements

- Python 3.x
- MySQL Server
- SQLite
- `mysql-connector-python` library for Python

### Install Required Libraries

Run the following command to install the required library:

```bash
pip install mysql-connector-python
```
---

### Database Setup
-- MySQL Setup
-- Create a database in your MySQL server:

```sql

CREATE DATABASE personnel_db;
Configure the MySQL username and password in pyserver.py:
```
```python

mysql.connector.connect(
    host="localhost",
    user="root",  # Your MySQL username
    password="password",  # Your MySQL password
    database="personnel_db"
)
```
### Usage
Start the Server and Start the Command Interface  
Run main.py to start the server. The server will handle client connections:

```bash
python main.py
```

### Start the Client
Run pyclient.py to start a client instance. You can run multiple clients to connect to the server:

```bash
python pyclient.py
```

### Project Structure
```
├── main.py:    # is the file to start the server side.
├── pyserver.py:    # Server application. Manages communication with clients and database operations.
├── pyclient.py:    #Client application. Processes commands from the server and saves and deletes data in the SQLite database.
├── messageslist.py:   # Creates a table in the MySql database for messages and adds data to it to be sent to clients.
├── personel.py:   # Creates a table in the MySql database for the personnel and adds data to it to be sent to the clients.
├── clientslist.py:    # Creates a table in the MySql database to keep the created clients up to date.
├── hlib.py:   # Contains auxiliary functions such as logging.
├── .env:  # Stores environment variables.
├── logdataClient.txt: # Logs after Client startup.
├── logdataServer.txt: # Logs after Server startup.
├── README.md:       # Documentation and usage guide for the project.
```



