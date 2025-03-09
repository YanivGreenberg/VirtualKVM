import socket
import sys


def create_server(listening_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind('', listening_port)
        server_socket.listen(2)
        print(f"server is listening on port {listening_port}")
        create_connection(server_socket)
    except Exception as e:
        print(e)
        sys.exit(2)


def create_connection(server_socket):
    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"connection was made with the address {client_address}")
            data = client_socket.recv(1024)
            if data is not None:
                handle_data(data)
        except KeyboardInterrupt:
            server_socket.close()
            print(f"server shutting down")
            sys.exit(1)         
    server_socket.close()


def handle_data(data):
    pass


if __name__ == "__main__":
    create_server(5555)