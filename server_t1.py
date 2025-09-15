from socket import *
serverPort = int(input("Enter port number: "))
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

clients_new_file_size = {}
clients_new_file_id   = {}

while True:
   connectionSocket, addr = serverSocket.accept()


   request = connectionSocket.recv(4096).decode()
   print(f"Receiving file from {addr}")
   if request.strip().upper().startswith('PUT'):
      try:
         parts = request.split(' ', 3)
         if len(parts) < 4:
            print(f"Comando PUT mal formatado recebido: {request}")
         else:
            _, filename, total_size_str, chunk = parts
            total_size = int(total_size_str)

            import os
            if not os.path.exists('uploads'):
               os.makedirs('uploads')

            if addr not in clients_new_file_size:
               clients_new_file_size[addr] = total_size
               if addr not in clients_new_file_id:
                  clients_new_file_id[addr] = 0
               else:
                  clients_new_file_id[addr] += 1

            file_id = clients_new_file_id[addr]
            file_path = f'uploads/{addr}_{filename}'
            with open(file_path, 'a', encoding='utf-8') as file:
               file.write(chunk)

            clients_new_file_size[addr] -= len(chunk)

            if clients_new_file_size[addr] <= 0:
               print(f"File upload complete: {file_path}")
               clients_new_file_id[addr] += 1
               del clients_new_file_size[addr]
      except Exception as e:
         print(f"Erro ao processar comando PUT: {e}\nConteúdo recebido: {request}")

   elif request.startswith('LIST'):
         import os
         files = os.listdir('uploads')
         response = ''
         for file in files:
            if file.startswith(f"{addr}"):
               response += file + ' '
         connectionSocket.send(response.encode())
   connectionSocket.close()

