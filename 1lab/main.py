import os
import struct
import socket
import json
from pprint import pprint
import threading


PORT = 64996
HOST = "localhost"


class SizeProtocol():

    MSGSIZE = 16

    def send(self, connected_socket, msg):
        connected_socket.send(struct.pack('I', len(msg)))
        connected_socket.sendall(msg.encode())

    def recv(self, connected_socket):
        msg_size, = struct.unpack('I', connected_socket.recv(struct.calcsize('I')))
        result = b''
        while len(result) < msg_size:
            result += connected_socket.recv(min(self.MSGSIZE, msg_size - len(result)))
        return result.decode()


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.protocol = SizeProtocol()
        self.host = host
        self.port = port

    def get_dirs(self):
        result = {}
        paths = os.environ.get('PATH').split(os.pathsep)

        for dir in paths:
            if os.path.isdir(dir):
                files = os.listdir(dir)  # список всех файлов в директории
                exe_files = [f for f in files if os.access(os.path.join(dir, f), os.X_OK)]
                if len(exe_files) != 0:
                    result[dir] = exe_files
        return result

    def save_to_json(self, dictionary, filename):
        with open(filename, "w") as fh:
            json.dump(dictionary, fh)

    def handle_client(self, client_socket):
        request = self.protocol.recv(client_socket)

        if request == 'GET_FILE':
            self.protocol.send(client_socket, f'{self.get_dirs()}')
        elif request.split()[0] == 'SET' and len(request.split()) == 3:
            os.environ[request.split()[1]] = request.split()[2]
            self.protocol.send(client_socket, 
                               f'Variable is set: {request.split()[1]} = {request.split()[2]}')
        else:
            self.protocol.send(client_socket, 'Unknown command')
        client_socket.close()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(1)
        while True:
            client, _ = server_socket.accept()
            self.handle_client(client)


class Client:
    def __init__(self, host=HOST, port=PORT):
        self.protocol = SizeProtocol()
        self.host = host
        self.port = port

    def send_command(self, command):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))
        self.protocol.send(client_socket, command)
        answer = self.protocol.recv(client_socket)
        pprint(answer)
        client_socket.close()


def main():
    server = Server()

    ##
    server_thread = threading.Thread(target=server.start_server)
    server_thread.daemon = True
    server_thread.start()
    ##

    client = Client()

    print('''Возможные команды: \n
          1. GET_FILE - Для получения информации об исполняемых файлас\n
          2. SET <VAR> <VALUE> - Для установления переменных окружения\n
          3. EXIT - Выход''')
    command = input('Введите команду: ')
    while command != 'EXIT':

        client.send_command(command)
        command = input('Введите команду: ')


if __name__ == "__main__":
    main()
