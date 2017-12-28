import socket
import threading

HOST = '127.0.0.1'
PORT = 17071


class TCP:
    def __init__(self):
        self.players = {}
        self.run = True

    def close(self, sock: socket.socket, data: bytes):
        print('Close', sock.getpeername())
        sock.close()
        del self.players[sock]
        for k in self.players.keys():
            k.send(data)

    def listen(self, sock: socket.socket):
        data_exit = b''
        while self.run:
            try:
                data = sock.recv(1024)
            except ConnectionResetError:
                sock.close()
                del self.players[sock]
                return
            if len(data) == 0:
                sock.close()
                del self.players[sock]
                return
            d = int(data[0])
            label = int(data[d + 1])
            if label == 3:
                # New New
                pass
            elif label == 1:
                # New
                for k, v in self.players.items():
                    if v is not None:
                        sock.send(v)
                    if sock != k:
                        k.send(data)
                self.players[sock] = data
                data_exit = data[0:d + 1] + (2).to_bytes(length=1, byteorder='big', signed=False)
                break

        while self.run:
            try:
                data = sock.recv(1024)
            except ConnectionResetError:
                self.close(sock, data_exit)
                return
            if len(data) == 0:
                self.close(sock, data_exit)
                return
            d = int(data[0])
            label = int(data[d + 1])
            if label == 0:
                # New Message
                pass
            elif label == 2:
                self.close(sock, data_exit)
                return
            elif label == 4:
                # Reset player
                self.players[sock] = data[0:d + 1] + \
                                     (1).to_bytes(length=1, byteorder='big', signed=False) + data[d + 2:]

            for k in self.players.keys():
                if sock != k:
                    k.send(data)

        sock.close()

    def run_serv(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen(2)
        print("Starting TCP server on %s:%d" % (HOST, PORT))
        while self.run:
            try:
                client_sock, addr = sock.accept()
            except KeyboardInterrupt:
                self.run = False
                break
            print('New client', addr)
            self.players[client_sock] = None
            threading.Thread(target=self.listen, args=(client_sock,)).start()


if __name__ == '__main__':
    TCP().run_serv()
