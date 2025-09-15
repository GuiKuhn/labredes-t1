from socket import *
serverName = input("Enter server IP address: ")
serverPort = int(input("Enter server port number: "))
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
while True:
    command = input("Enter command: ")
    if command == 'QUIT':
        break
    if command.startswith('PUT'):
        filepath = command.split()[1]
        filename = filepath.split('/')[-1]
        try:
            with open(filepath, 'r') as file:
                content = file.read()

            content_size = len(content)

            for i in range(0, content_size, 1024):
                chunk = content[i:i+1024]
                payload = f'PUT {filename} {len(content)} {chunk}'.encode()
                clientSocket.send(payload)
        except FileNotFoundError:
            print("File not found.")
        
    elif command.startswith('LIST'):
        clientSocket.send(command.encode())
        response = clientSocket.recv(4096).decode()
        print("Files on server:\n", response)
clientSocket.close()
