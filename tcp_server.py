import socket
import threading
from peewee import *
import logging
from datetime import date

HOST = '0.0.0.0'
PORT = 17071

db = MySQLDatabase("admin_test",
                   host="188.226.185.13",
                   port=3306,
                   user="admin_test",
                   passwd="111111")

# db = MySQLDatabase("rstabhuymg",
#                    host="188.166.93.63",
#                    port=8082,
#                    user="rstabhuymg",
#                    password="rq33hMdn5M")

logger = logging.getLogger("tcp_server")
logger.setLevel(logging.INFO)
# create the logging file handler
fh = logging.FileHandler("server_activity.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
fh.setFormatter(formatter)
# add handler to logger object
logger.addHandler(fh)

class User(Model):
    user_login = TextField()
    class Meta:
        database = db
# User.create_table()

class TCP:
    def __init__(self):
        self.players = {}
        self.run = True

    def close(self, sock: socket.socket, data: bytes):
        print('Close', sock.getpeername())
        logger.info('Close {}'.format(sock.getpeername()))
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
            login = data[1:d + 1]
            label = int(data[d + 1])
            if label == 3:
                user = User
                print(user)
                try:
                    tupl = user.select().where(user.user_login == login).get()
                except:
                    tupl = 0

                if tupl == 0:
                    user = User.create(user_login=login)
                    logger.info("New client has been created. Login: {}".format(login.decode("utf-8")))
                    sock.sendto((1).to_bytes(1, 'big'), sock.getpeername())  # в базе нет, логин создали
                else:
                    logger.info("db already has this name".format(login.decode("utf-8")))
                    sock.sendto((0).to_bytes(1, 'big'), sock.getpeername())  # в базе есть, ошибка
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
        logger.info("Starting TCP server on %s:%d" % (HOST, PORT))
        while self.run:
            try:
                client_sock, addr = sock.accept()
            except KeyboardInterrupt:
                self.run = False
                break
            print('New client', addr)
            logger.info('New client {}'.format(addr))
            self.players[client_sock] = None
            threading.Thread(target=self.listen, args=(client_sock,)).start()


if __name__ == '__main__':
    TCP().run_serv()
