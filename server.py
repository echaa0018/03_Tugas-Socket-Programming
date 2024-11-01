import socket
import threading
import queue
import os

# FUNCTION DECLARATION AND MORE
messages = queue.Queue()
clients = {}
client_tags = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

HISTORY_FILE = "chat_history.txt"

# Fungsi untuk memuat riwayat pesan dari file
def load_history(addr):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            for line in f:
                server.sendto(line.encode(), addr)

# Fungsi untuk menyimpan pesan ke file
def save_message(message):
    with open(HISTORY_FILE, "a") as f:
        f.write(message + "\n")

def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except Exception as e:
            print(f"Receive error: {e}")

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded_message = message.decode()
            print(decoded_message)
            
            if addr not in clients:
                if decoded_message.startswith("SIGNUP_TAG:"):
                    name = decoded_message.split(":", 1)[1].strip()
                    if name in client_tags: # check if name is already in the chatroom
                        server.sendto("NAME_TAKEN".encode(), addr) # send to a message to the client that name is taken
                    else: # if name is unique, register the name and add it to the clients list and array
                        clients[addr] = name
                        client_tags.append(name)
                        for client in clients: # send the message to the client that someone has joined the chatroom
                            server.sendto(f"{name} joined!".encode(), client)
            else:
                if decoded_message.startswith("QUIT_TAG:"): # when a client quits the chatroom
                    name = clients[addr]
                    for client in clients: # send to the client that someone left the chatroom
                        server.sendto(f"{name} has left the chatroom.".encode(), client)
                    del clients[addr] # removing the name from the array and tuples
                    client_tags.remove(name)
                else: # send the message to the client
                    for client in clients:
                        if client != addr:
                            server.sendto(message, client)

# PROGRAM
t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()