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
shift = 3  # Shift for Caesar cipher

def caesar_encrypt(message, shift):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            shift_base = ord('a') if char.islower() else ord('A')
            encrypted_message += chr((ord(char) - shift_base + shift) % 26 + shift_base)
        else:
            encrypted_message += char
    return encrypted_message

def caesar_decrypt(message, shift):
    return caesar_encrypt(message, -shift)

# Fungsi untuk memuat riwayat pesan dari file
def load_history(addr):
    try:
        with open(HISTORY_FILE, "r") as f:
            for line in f:
                encrypted_line = caesar_encrypt(line.strip(), shift)
                server.sendto(encrypted_line.encode(), addr)
    except FileNotFoundError:
        pass  # Skip if no history file exists yet

def save_message(message):
    with open(HISTORY_FILE, "a") as f:
        f.write(message + "\n")

def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            print(f"Received message from {addr}: {message.decode()}")  # Debug print
            messages.put((message, addr))
        except Exception as e:
            print(f"Receive error: {e}")

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded_message = caesar_decrypt(message.decode(), shift)
            print(f"Broadcasting message from {addr}: {decoded_message}")  # Debug print
            
            if addr not in clients:
                if decoded_message.startswith("SIGNUP_TAG:"):
                    name = decoded_message.split(":", 1)[1].strip()
                    if name in client_tags:  # check if name is already in the chatroom
                        encrypted_response = caesar_encrypt("NAME_TAKEN", shift)
                        server.sendto(encrypted_response.encode(), addr)
                    else:
                        clients[addr] = name
                        client_tags.append(name)
                        load_history(addr)
                        for client in clients:
                            join_message = f"{name} joined!"
                            server.sendto(caesar_encrypt(join_message, shift).encode(), client)
                        save_message(f"{name} joined!")
            else:
                if decoded_message.startswith("QUIT_TAG:"):  # when a client quits the chatroom
                    name = clients[addr]
                    for client in clients:  # notify clients that someone left the chatroom
                        leave_message = f"{name} has left the chatroom."
                        server.sendto(caesar_encrypt(leave_message, shift).encode(), client)
                    del clients[addr]
                    client_tags.remove(name)
                    save_message(f"{name} has left the chatroom.")
                else:  # send the message to clients
                    for client in clients:
                        if client != addr:
                            server.sendto(caesar_encrypt(decoded_message, shift).encode(), client)
                    save_message(decoded_message)

# PROGRAM
t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start()
