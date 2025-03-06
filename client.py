import socket


def create_connection(server_port):
    server_host = 'localhost'
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_host, server_port)
        print(f"[*] Connected to server at {server_host}:{server_port}")
        

    except Exception as e:
        print(f"Error: {e}")  


if __name__ == "__main__":
    create_connection(5555)
