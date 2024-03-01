import socket
import struct
import threading
import time

list_of_clients_and_sockets = []
lock = threading.Lock()


def send_disconnected_client(c_addr):
    print(f"Client {c_addr} disconnected!")
    for sock in list_of_clients_and_sockets:
        sock[0].send("left".encode('ascii'))
        sock[0].send(c_addr[0].encode('ascii'))
        time.sleep(0.3)
        sock[0].send(struct.pack("!i", c_addr[1]))


def send_connected_client(c_addr):
    print(f"Client {c_addr} connected!")
    for sock in list_of_clients_and_sockets:
        if sock[1] != c_addr:
            sock[0].send("new".encode('ascii'))
            sock[0].send(c_addr[0].encode('ascii'))
            time.sleep(0.3)
            sock[0].send(struct.pack("!i", c_addr[1]))


def handle_client(client_socket: socket.socket, c_addr):
    global list_of_clients_and_sockets, lock
    print(f"Client connected from {c_addr}")
    lock.acquire()
    client_socket.send(struct.pack("!i", len(list_of_clients_and_sockets)))
    print("Sent length of list of clients!")
    for clients in list_of_clients_and_sockets:
        client_socket.send(clients[1][0].encode('ascii'))
        time.sleep(0.3)
        client_socket.send(struct.pack("!i", clients[1][1]))
    list_of_clients_and_sockets.append((client_socket, c_addr))
    lock.release()
    print("Sent the initial list to the client!")
    send_connected_client(c_addr)
    while True:
        data = client_socket.recv(1024).decode("ascii")
        if data == "QUIT":
            list_of_clients_and_sockets.remove((client_socket, c_addr))
            send_disconnected_client(c_addr)
            break
    client_socket.close()


def main():
    global list_of_clients_and_sockets
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 7000))
    sock.listen(5)
    print("Socket created and listening for incoming clients...")
    sock.settimeout(20)
    while True:
        try:
            client_socket, c_addr = sock.accept()
        except TimeoutError:
            break
        client_handler = threading.Thread(target=handle_client, args=(client_socket, c_addr))
        client_handler.start()
    sock.close()


if __name__ == "__main__":
    main()
