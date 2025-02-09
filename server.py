import socket

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = "0.0.0.0"
    port = 40600

    server_socket.bind((host,port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection received from {client_address}")


if __name__ == "__main__":
    #start_server()
    num = input("enter a number")
    print(num)