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
broadcast_sockets = set()


def send_broadcast():
    """
    Format:
        users:<user1>,<user2>,<user3>\r\n
        messages:\r\n
        <user1>::<message1>\r\n
        <user2>::<message2>\r\n
    """
    msg_lines = []
    msg_lines.append("users:" + users_as_str() + "\r\n")
    msg_lines.append("messages:\r\n")

    for line in messages_as_str():
        msg_lines.append(line)

    msg_str = "".join(msg_lines)

    for listener in broadcast_sockets:
        listener.send(msg_str.encode())


def messages_as_str():
    msg_list = []

    for msg in message_log:
        msg_as_str = "{}::{}".format(msg[0], msg[1])
        msg_list.append(msg_as_str)

    return "\r\n".join(msg_list)
    
def users_as_str():
    return ",".join(users)


def send_message_log(connection_socket):
    msgs_as_str = messages_as_str() + "\r\n"
    connection_socket.send(msgs_as_str.encode())

    
def send_users(connection_socket):
    users_str = users_as_str() + "\r\n"
    connection_socket.send(users_str.encode())


def process_client_messages(connection_socket, username):
    connection_open = True
    while connection_open:
    
        message = connection_socket.recv(1024).decode().rstrip("\r\n")
        
        if message == "get messages":
                send_message_log(connection_socket)

        if message == "get users":
                send_users(connection_socket)

        if message[0:5] == "send ":
            user_msg = message[5:]
            message_log.append((username, user_msg))
            connection_socket.send(b"message received\r\n")
            send_broadcast()
            
        elif message == "quit":
            connection_socket.send(b"goodbye\r\n")
            connection_open = False

    connection_socket.close()

    
def handle_connection(connection_socket):
    # Handshake
    message = connection_socket.recv(1024).decode().rstrip("\r\n")
    prefix  = message.split()[0]

    if prefix == "hello":
        username = message[6:] # Exclude "hello" of message: "hello <username>"
        connection_socket.send("welcome {}\r\n".format(username).encode())

        if username not in users:
            users.append(username) # TODO: Maybe use a set for users instead?

        process_client_messages(connection_socket, username)

    elif prefix == "listen":
        broadcast_sockets.add(connection_socket)
        connection_socket.send(b"listener added\r\n")


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
