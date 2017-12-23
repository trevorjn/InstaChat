import socket
import time

PORT = 10101
HOST = "localhost"

def process_user_input(client_socket, username):
    user_connected = True

    while user_connected:
        # Show user interface
        users, messages = get_interface_data(client_socket)
        display_interface(users, messages)
    
        user_msg = input("Enter message (or QUIT): ")
        if user_msg.lower() == "quit":
            user_connected = False
        else:
            client_socket.send("send {}\r\n".format(user_msg).encode())
            client_socket.recv(1024)

def get_interface_data(client_socket):
    # Get users
    client_socket.send(b"get users\r\n")
    users = client_socket.recv(1024).decode().rstrip("\r\n").split(",")
    
    # Get messages
    client_socket.send(b"get messages\r\n")
    response = client_socket.recv(1024).decode()
    
    messages = []

    response_msgs = response.rstrip("\r\n").split("\r\n")
    if response_msgs[0] != "":
        for msg in response.rstrip("\r\n").split("\r\n"):
            split_msg = msg.split("::")
            messages.append((split_msg[0], split_msg[1]))

    return users, messages

def display_interface(users, messages):
    print("\n### Users ###")
    for user in users:
        print(user)

    print("\n### Messages ###")
    for msg in messages:
          print("{}: {}".format(msg[0], msg[1]))

if __name__ == "__main__":
    print("Connecting to server...")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print("Connected!")

    username = input("Hello, please enter a username: ")
    client_socket.send("hello {}\r\n".format(username).encode())
    client_socket.recv(1024)

    process_user_input(client_socket, username)
