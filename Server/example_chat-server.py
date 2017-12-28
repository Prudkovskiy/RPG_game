"""
Низкоуровневая реализация TCP-сервера, работающего с множеством клиентов, используя потоки.
"""
import threading
import queue
import socket
import json


HOST = "127.0.0.1"
PORT = 9999
send_queues = {}
lock = threading.Lock()


def handle_client_recv(sock, addr):
    """
    Receive messages from client and broadcast them to
    other clients until client disconnects
    """
    while True:
        data = sock.recv(4096)
        print("Got data from", sock.getpeername(), data.decode())
        if not data:
            handle_disconnect(sock)
            break

        broadcast(data, addr, sock.fileno())


def handle_client_send(sock, q):
    """ Monitor queue for new messages, send them to client as
        they arrive """
    while True:
        data = q.get()
        if data is None:
            break
        try:
            res = json.dumps(data)
            sock.send(res.encode())
        except (IOError, ):
            handle_disconnect(sock)
            break


def broadcast(data, addr, info):
    """
    Add message to each connected client's send queue
    """
    print("Broadcast:", data.decode())
    st = json.loads(data.decode())
    with lock:
        for q in send_queues.keys():
            if q != info:
                send_queues[q].put([addr].extend(st))


def handle_disconnect(sock):
    """
    Ensure queue is cleaned up and socket closed when a client
    disconnects
    """
    fd = sock.fileno()
    with lock:
        # Get send queue for this client
        q = send_queues.get(fd, None)

    # If we find a queue then this disconnect has not yet
    # been handled
    if q:
        q.put(None)
        del send_queues[fd]
        addr = sock.getpeername()
        res = json.dumps([addr, 'disconnected'])
        sock.send(res.encode())
        print('Client {} disconnected'.format(addr))
        sock.close()


def main():
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((HOST, PORT))
    listen_sock.listen(5)

    while True:
        client_sock, addr = listen_sock.accept()
        q = queue.Queue()

        with lock:
            send_queues[client_sock.fileno()] = q
            res = json.dumps([addr, 'connected'])
            client_sock.send(res.encode())
        threading.Thread(
            target=handle_client_recv,
            args=[client_sock, addr], daemon=True
        ).start()
        threading.Thread(
            target=handle_client_send,
            args=[client_sock, q], daemon=True
        ).start()
        print('Connection from {}'.format(addr))


if __name__ == '__main__':
    main()