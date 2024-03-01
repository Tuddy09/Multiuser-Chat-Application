import socket
import struct
import threading
import time

number_of_clients = 0
list_of_clients = []

lock = threading.Lock()


def server_handler(s_socket: socket.socket):
    global list_of_clients, number_of_clients
    try:
        while True:
            data = s_socket.recv(1024).decode("ascii")
            host = s_socket.recv(1024)
            list_of_data = host.rsplit(bytes(1))
            host = list_of_data[0]
            host = host.decode("ascii")
            port = struct.unpack("!i", s_socket.recv(1024))[0]
            if data == "new":
                number_of_clients += 1
                list_of_clients.append((host, port))
                print(f"Client {host, port} has connected!")
            elif data == "left":
                number_of_clients -= 1
                list_of_clients.remove((host, port))
                print(f"Client {host, port} has disconnected!")
    except ConnectionAbortedError:
        print("Closing connection...")
        exit(0)


def message_receiver(udp_socket):
    time.sleep(1)
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)
            if not data:
                # If data is empty, the socket is closed
                break
            data = data.decode("ascii")
            print(f"Received {data} from client {addr}")
        except BlockingIOError:
            # No data available, continue with the loop
            time.sleep(0.1)
        except ConnectionResetError:
            # Handle the case where the connection is forcibly closed
            print("Connection forcibly closed by the remote host.")
            break
        except OSError:
            exit(0)


def main():
    global list_of_clients, number_of_clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(('127.0.0.1', 7000))
    print("Client connected to the server!")
    data = server_socket.recv(1024)
    number_of_clients = struct.unpack("!i", data)[0]
    for _ in range(number_of_clients):
        host = server_socket.recv(1024).decode("ascii")
        port = struct.unpack("!i", server_socket.recv(1024))[0]
        list_of_clients.append((host, port))
    print(f"Got initial list of clients: {list_of_clients}")
    refresh_list = threading.Thread(target=server_handler, args=(server_socket,))
    refresh_list.start()
    my_port = server_socket.getsockname()[1]
    print(f"My port is {my_port}")
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('127.0.0.1', int(my_port)))
    udp_socket.setblocking(False)
    chat_handler = threading.Thread(target=message_receiver, args=(udp_socket,))
    chat_handler.start()
    while True:
        message = input("Please input the message or QUIT if you want to disconnect:")
        if message == "QUIT":
            server_socket.send("QUIT".encode("ascii"))
            break
        lock.acquire()
        for client in list_of_clients:
            udp_socket.sendto(message.encode("ascii"), client)
        lock.release()
    udp_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
