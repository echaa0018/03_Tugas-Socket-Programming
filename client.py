import socket
import threading
import random
import sys
import os

# FUNCTION AND OTHER DELCARATIONS
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

correct_password = "luvmakima" # password to enter the chatroom Makima <3

def authentication(): # checks is the user knows the password
    password = input("Password (1 attempt): ")
    if password != correct_password:
        print("Incorrect Password, Goodbye.")
        sys.exit()
    else:
        print("Correct Password, Please enter the necessary information to access the chatroom")

def get_server_details(): # get the server detail from the client
    server_ip = input("IP address: ")
    server_port = int(input("Server port: "))
    return server_ip, server_port

def sign_up(): # check if there are duplicate usernames or not
    global name
    while True:
        name = input("Nickname: ")
        client.sendto(f"SIGNUP_TAG: {name}".encode(), (server_ip, server_port))
        message, _ = client.recvfrom(1024)
        decoded_message = message.decode()
        
        if decoded_message == "NAME_TAKEN": # if name is already in the chatroom
            print(f"\033[91mYou cannot have two {name}'s in the chatroom, please choose another name.\033[0m") 
        else: # name is already unique
            clear_terminal()
            print(f"Welcome to the chatroom, {name}!!") 
            print()
            break

def receive(): # continuously receive messages from the server
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(f"\033[93m{message.decode()}\033[0m")
            print()
        except Exception as e:
            print("\033[91mPlease re-check your IP and port and run the program again.\033[0m")
            print(f"Receive error: {e}")

def clear_terminal(): # clearing the terminal for a cleaner experience
    if os.name == 'nt':
        os.system('cls')  # for windows
    else:
        os.system('clear')  # for macOS or Linux

# PROGRAM
clear_terminal()
authentication()
server_ip, server_port = get_server_details()
sign_up()
t = threading.Thread(target=receive)
t.start()
while True: # Loop for receiving and sending messages
    message = input("")
    print("\033[A\033[K", end="")
    if message == "!q": # client quits the chatroom
        client.sendto(f"QUIT_TAG: {name}".encode(), (server_ip, server_port))
        print("\033[36mYou have left the chatroom.\033[0m")
        print()
        break  # exit the loop
    else: # send message to the server and print it to the clients
        client.sendto(f"{name}: {message}".encode(), (server_ip, server_port))
        print(f"\033[36m{name}: {message}\033[0m")
        print()