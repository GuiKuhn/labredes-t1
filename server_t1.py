

# Imports necessários
import os
import threading
import time
from socket import *


# Diretórios para uploads e logs
UPLOADS_DIR = 'uploads'
LOGS_DIR = 'logs'
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


# Função para remover acentos dos logs
import unicodedata
def remove_acentos(txt):
   return ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')

# Função para registrar logs de cada conexão

# Função para registrar logs de cada conexão (agora por nome de usuário)
def log_connection(username, log_lines):
   timestamp = time.strftime('%Y%m%d_%H%M%S')
   log_file = os.path.join(LOGS_DIR, f'log_{username}_{timestamp}.txt')
   with open(log_file, 'w') as f:
      for line in log_lines:
         f.write(remove_acentos(line) + '\n')


def handle_client(connectionSocket, addr):
   """
   Função que trata cada cliente em uma thread.
   A primeira mensagem recebida deve ser o nome do usuário.
   Todos os arquivos e logs são identificados por esse nome.
   """
   log_lines = []
   start_time = time.time()
   total_received = 0
   total_sent = 0
   try:
      # Recebe o nome do usuário
      username_bytes = connectionSocket.recv(4096)
      if not username_bytes:
         connectionSocket.close()
         return
      username = username_bytes.decode(errors='ignore').strip()
      log_lines.append(f"[{time.strftime('%H:%M:%S')}] Usuario conectado: {username}")
      while True:
         # Recebe comando do cliente
         request = connectionSocket.recv(4096)
         if not request:
            break
         request_decoded = request.decode(errors='ignore')
         log_lines.append(f"[{time.strftime('%H:%M:%S')}] Recebido: {len(request)} bytes")
         total_received += len(request)
         if request_decoded.startswith('PUT'):
            # PUT filename filesize\n<filedata>
            try:
               header, filedata = request_decoded.split('\n', 1)
               _, filename, filesize = header.split()
               filesize = int(filesize)
            except Exception:
               connectionSocket.send(b'Invalid PUT format')
               total_sent += len('Invalid PUT format')
               continue
            # Salva arquivo com nome do usuario
            filepath = os.path.join(UPLOADS_DIR, f'{username}_{filename}')
            with open(filepath, 'wb') as f:
               f.write(filedata.encode())
               bytes_written = len(filedata.encode())
               while bytes_written < filesize:
                  chunk = connectionSocket.recv(min(4096, filesize - bytes_written))
                  if not chunk:
                     break
                  f.write(chunk)
                  bytes_written += len(chunk)
                  log_lines.append(f"[{time.strftime('%H:%M:%S')}] Recebido: {len(chunk)} bytes (arquivo)")
                  total_received += len(chunk)
            connectionSocket.send(b'Upload complete')
            total_sent += len('Upload complete')
            log_lines.append(f"[{time.strftime('%H:%M:%S')}] Enviado: Upload complete")
         elif request_decoded.startswith('LIST'):
            # Lista arquivos do usuario (apenas nomes originais)
            files = os.listdir(UPLOADS_DIR)
            user_files = [f[len(username)+1:] for f in files if f.startswith(f'{username}_')]
            response = '\n'.join(user_files) if user_files else 'No files.'
            connectionSocket.send(response.encode())
            total_sent += len(response)
            log_lines.append(f"[{time.strftime('%H:%M:%S')}] Enviado: {len(response)} bytes (lista)")
         elif request_decoded.startswith('QUIT'):
            # Cliente deseja encerrar
            connectionSocket.send(b'Connection closed')
            total_sent += len('Connection closed')
            log_lines.append(f"[{time.strftime('%H:%M:%S')}] Enviado: Connection closed")
            break
         else:
            connectionSocket.send(b'Invalid command')
            total_sent += len('Invalid command')
            log_lines.append(f"[{time.strftime('%H:%M:%S')}] Enviado: Invalid command")
   except Exception as e:
      log_lines.append(f"Erro: {e}")
   finally:
      end_time = time.time()
      duration = end_time - start_time
      bps_recv = total_received / duration if duration > 0 else 0
      bps_sent = total_sent / duration if duration > 0 else 0
      # Log por usuario
      log_lines.append(f"Conexao encerrada. Duracao: {duration:.2f}s, Recebido: {total_received} bytes, Enviado: {total_sent} bytes, Taxa RX: {bps_recv:.2f} Bps, TX: {bps_sent:.2f} Bps")
   log_connection(username, log_lines)
   connectionSocket.close()


# Função principal do servidor
def main():
   serverPort = int(input("Enter port number: "))
   serverSocket = socket(AF_INET,SOCK_STREAM)
   serverSocket.bind(('',serverPort))
   serverSocket.listen(5)
   print('The server is ready to receive')
   while True:
      connectionSocket, addr = serverSocket.accept()
      print(f"Connection from {addr}")
      t = threading.Thread(target=handle_client, args=(connectionSocket, addr))
      t.daemon = True
      t.start()

if __name__ == "__main__":
   main()

