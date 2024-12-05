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



Multi-Threaded-Server-Client-Application

