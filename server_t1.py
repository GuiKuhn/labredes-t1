from socket import *
serverPort = int(input("Enter port number: "))
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.listen(1)
serverSocket.bind(('',serverPort))
print('The server is ready to receive')

clients_new_file_size = {}
clients_new_file_id   = {}

while True:
   connectionSocket, addr = serverSocket.accept()

   request = connectionSocket.recv(1024).decode()
   if request.startswith('PUT'):
         parts = request.split(' ', 2)
         filename = parts[0].split()[1]

         total_size = int(parts[1])
         chunk = parts[2]
   
         if addr not in clients_new_file_size:
            clients_new_file_size[addr] = total_size
            if addr not in clients_new_file_id:
               clients_new_file_id[addr] = 0
            else:
               clients_new_file_id[addr] += 1

         file_id = clients_new_file_id[addr]
         with open(f'uploads/{addr}_{filename}', 'a') as file:
            file.write(chunk)
   
         clients_new_file_size[addr] -= len(chunk)
   
         if clients_new_file_size[addr] <= 0:
            print(f"File upload complete: uploaded_file_{file_id}.{file_ext}")
            clients_new_file_id[addr] += 1
            del clients_new_file_size[addr]

   elif request.startswith('LIST'):
         import os
         files = os.listdir('uploads')
         response = ''
         for file in files:
            if file.startswith(f"{addr}"):
               response += file + ' '
         connectionSocket.send(response.encode())
   connectionSocket.close()

