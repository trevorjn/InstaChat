"""
Protocol (c=client, s=server):
c: hello <username>\r\n
s: welcome <username>\r\n
c: get messages
s: <user1>: <message1>\r\n
   <user2>: <message2>\r\n
c: send <message3>\r\n
s: message received\r\n
c: get messages
s: <user1>::<message1>\r\n
   <user2>::<message2>\r\n
   <user3>::<message3>\r\n
c: quit
s: goodbye
"""

import socket
import threading


PORT = 10101
message_log = []
users = []
new_message = False


def process_client_messages(connection_socket, username):
    connection_open = True
    while connection_open:
        
        message = connection_socket.recv(1024).decode().rstrip("\r\n")
    
        if message == "get messages":
            msg_list = []
            for msg in message_log:
                msg_as_str = "{}::{}\r\n".format(msg[0], msg[1])
                msg_list.append(msg_as_str)
            msgs_as_str = "".join(msg_list) + "\r\n"
            connection_socket.send(msgs_as_str.encode())

        if message == "get users":
            users_as_str = ",".join(users) + "\r\n" # consider storing users as list instead
            connection_socket.send(users_as_str.encode())

        if message[0:5] == "send ":
            user_msg = message[5:]
            message_log.append((username, user_msg))
            connection_socket.send(b"message received\r\n")
                
        elif message == "quit":
            connection_socket.send(b"goodbye\r\n")
            connection_open = False

    connection_socket.close()

        
def handle_connection(connection_socket):
    # Handshake
    message = connection_socket.recv(1024).decode()
    username = message.rstrip("\r\n")[6:] # Exclude "hello" of message: "hello <username>"
    connection_socket.send("welcome {}\r\n".format(username).encode())

    if username not in users:
        users.append(username)

    process_client_messages(connection_socket, username)
    

if __name__ == "__main__":
    # Setup TCP server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    server_socket.listen()

    while True:
        print("Ready to serve...")
        
        connection_socket, addr = server_socket.accept()

        connection_thread = threading.Thread(target=handle_connection, daemon=True, args=(connection_socket,))
        connection_thread.start()

    server_socket.close()
