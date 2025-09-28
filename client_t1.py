from socket import *
import os

serverName = input("Enter server IP address: ")
serverPort = int(input("Enter server port number: "))
username = input("Enter your username: ").strip()
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
# Envia nome do usuário como primeira mensagem
clientSocket.send(username.encode())

while True:
    command = input("Enter command: ")
    if command == "QUIT":
        clientSocket.send(command.encode())
        response = clientSocket.recv(4096).decode()
        print(response)
        break
    if command.startswith("PUT"):
        filepath = command.split()[1]
        filename = os.path.basename(filepath)
        try:
            filesize = os.path.getsize(filepath)
            header = f"PUT {filename} {filesize}\n".encode()
            # Envia cabeçalho primeiro
            clientSocket.sendall(header)
            # Envia arquivo em partes
            with open(filepath, "rb") as file:
                sent = 0
                while sent < filesize:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    clientSocket.sendall(chunk)
                    sent += len(chunk)
            # Só espera resposta após envio completo
            response = clientSocket.recv(4096).decode(errors="ignore")
            print(response)
        except FileNotFoundError:
            print("File not found.")
    elif command.startswith("LIST"):
        clientSocket.send(command.encode())
        response = clientSocket.recv(4096).decode()
        print("Files on server:\n", response)
clientSocket.close()
