import socket
import threading
import random
import sys

# FUNCTION AND OTHER DELCARATIONS
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

correct_password = "luvmakima" # password to enter the chatroom Makima <3
shift = 3  # Shifting untuk cipher Caesar

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
        encrypted_name = caesar_encrypt(f"SIGNUP_TAG: {name}", shift)
        client.sendto(encrypted_name.encode(), (server_ip, server_port))
        message, _ = client.recvfrom(1024)
        decoded_message = caesar_decrypt(message.decode(), shift)
        
        if decoded_message == "NAME_TAKEN": # if name is already in the chatroom
            print(f"\033[91mYou cannot have two {name}'s in the chatroom, please choose another name.\033[0m") 
        else: # name is already unique
            print(f"Welcome to the chatroom, {name}!!") 
            print()
            break

def receive(): # continuously receive messages from the server
    while True:
        try:
            message, _ = client.recvfrom(1024)
            decrypted_message = caesar_decrypt(message.decode(), shift)
            print(f"\033[93m{message.decode()}\033[0m")
            print()
        except Exception as e:
            print("\033[91mPlease re-check your IP and port and run the program again.\033[0m")
            print(f"Receive error: {e}")
 # for macOS or Linux

# PROGRAM
authentication()
server_ip, server_port = get_server_details()
sign_up()
t = threading.Thread(target=receive)
t.start()
while True: # Loop for receiving and sending messages
    message = input("")
    print("\033[A\033[K", end="")
    if message == "!q": # client quits the chatroom
        encrypted_message = caesar_encrypt(f"QUIT_TAG: {name}", shift)
        client.sendto(f"QUIT_TAG: {name}".encode(), (server_ip, server_port))
        print("\033[36mYou have left the chatroom.\033[0m")
        print()
        break  # exit the loop
    else: # send message to the server and print it to the clients
        encrypted_message = caesar_encrypt(f"{name}: {message}", shift)
        client.sendto(f"{name}: {message}".encode(), (server_ip, server_port))
        print(f"\033[36m{name}: {message}\033[0m")
        print()