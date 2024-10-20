import socket
import threading
import queue

messages = queue.Queue()
clients = {}

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

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
                # If the message starts with SIGNUP_TAG, register the client
                if decoded_message.startswith("SIGNUP_TAG:"):
                    name = decoded_message.split(":", 1)[1].strip()
                    clients[addr] = name
                    # Notify all clients that the user has joined
                    for client in clients:
                        server.sendto(f"{name} joined!".encode(), client)
            else:
                # Check if the message is a quit message
                if decoded_message.startswith("QUIT_TAG:"):
                    name = clients[addr]
                    # Notify all clients that the user has left
                    for client in clients:
                        server.sendto(f"{name} has left the chatroom.".encode(), client)
                    del clients[addr]  # Remove the client from the list
                else:
                    # Regular message, broadcast to all clients
                    for client in clients:
                        if client != addr:  # Do not send the message back to the sender
                            server.sendto(message, client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()