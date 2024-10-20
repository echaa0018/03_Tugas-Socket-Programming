import socket
import threading
import random
import sys
import time

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

correct_password = "luvmakima"

def authentication():
    password = input("Password (1 attempt only): ")
    if password != correct_password:
        print("Incorrect Password, Goodbye")
        sys.exit()
    else:
        print("Correct Password, please wait")
        time.sleep(1)

authentication()

name = input("Nickname: ")

def get_server_details():
    """Get server IP and port from the user."""
    server_ip = input("Enter the server IP address: ")
    server_port = int(input("Enter the server port: "))
    return server_ip, server_port

server_ip, server_port = get_server_details()

def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except Exception as e:
            print(f"Receive error: {e}")

t = threading.Thread(target=receive)
t.start()

client.sendto(f"SIGNUP_TAG: {name}".encode(), (server_ip, server_port))

while True:
    message = input("")
    if message == "!q":
        # Send quit message to the server
        client.sendto(f"QUIT_TAG: {name}".encode(), (server_ip, server_port))
        print("You have left the chatroom.")
        break  # Exit the loop and terminate the client
    else:
        # Send the message to the server
        client.sendto(f"{name}: {message}".encode(), (server_ip, server_port))
        # Display the message on the client's own terminal
        print(f"{name}: {message}")