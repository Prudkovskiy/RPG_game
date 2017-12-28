import asyncio
import time

HOST = '127.0.0.1'
PORT = 17070


async def check_players(players: dict):
    while True:
        await asyncio.sleep(5*60)
        print('Garbage collection')
        time_now = time.time()
        for key, value in players.items():
            if time_now - value > 5*60:
                print('Delete ', key)
                del players[key]


class EchoServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, players: dict):
        super(EchoServerProtocol, self).__init__()
        self.players = players
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        if len(data) == 0:
            del self.players[addr]
        else:
            self.players[addr] = time.time()
            print(data, addr)
            for key in self.players.keys():
                if key != addr:
                    try:
                        self.transport.sendto(data, key)
                    except ConnectionResetError:
                        print(key)
                        del self.players[key]

    def error_received(self, exc):
        print(type(exc))
        return exc


def main():
    players = {}
    loop = asyncio.get_event_loop()
    print("Starting UDP server on %s:%d" % (HOST, PORT))

    # One protocol instance will be created to serve all client requests
    listen = loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(players),
        local_addr=(HOST, PORT)
    )

    transport, protocol = loop.run_until_complete(listen)
    loop.run_until_complete(check_players(players))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    transport.close()
    loop.close()
    print(players)


if __name__ == "__main__":
    main()
