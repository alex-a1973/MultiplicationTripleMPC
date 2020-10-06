import math
import random
import socket

class Server:
    MOD_CONST = 16384
    def __init__(self, ip, port):
        """
        Initializes a Server class which assigns a server socket as a data member. Server is provided an IP and a
        port.
        """
        # AF_INET refers to the address family IPv4, SOCK_STREAM means connection oriented TCP protocol
        self.ti_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ti_sock.bind((ip, port))
        self.ti_sock.listen(5)
        self.ti_sock.settimeout(10.0)
        
    def generate(self, x, y):
        """
        Generates secret shared values [a], [b], [c] and distributes shares of the secret shared values to two players
        Alice and Bob. The shares are in the format "a_player:b_player:c_player" where a, b, and c are shares for the 
        secret shared values and player represents either Alice or Bob. Also given an x and y it'll give x_alice, y_alice, 
        x_bob, and y_bob to Alice and Bob.
        """
        self.a = int(random.random() * self.MOD_CONST)
        self.b = int(random.random() * self.MOD_CONST)
        self.c = (self.a * self.b) % self.MOD_CONST
        print(f'Secret shares [a], [b], and [c]: {self.a}, {self.b}, {self.c}')

        self.alice_a = int(random.random() * self.MOD_CONST)
        self.alice_b = int(random.random() * self.MOD_CONST)
        self.alice_c = int(random.random() * self.MOD_CONST)
        self.alice_x = int(random.random() * self.MOD_CONST)
        self.alice_y = int(random.random() * self.MOD_CONST)

        self.bob_a = (self.a - self.alice_a) % self.MOD_CONST
        self.bob_b = (self.b - self. alice_b) % self.MOD_CONST
        self.bob_c = (self.c - self.alice_c) % self.MOD_CONST
        self.bob_x = (x - self.alice_x) % self.MOD_CONST
        self.bob_y = (y - self.alice_y) % self.MOD_CONST

        # Format data to be sent to Alice and Bob
        concat_alice = f'{self.alice_a}:{self.alice_b}:{self.alice_c}:{self.alice_x}:{self.alice_y}'
        concat_bob = f'{self.bob_a}:{self.bob_b}:{self.bob_c}:{self.bob_x}:{self.bob_y}'

        self.a_sock_conn, self.a_sock_addr = self.ti_sock.accept()
        print(f'Alice has connected from {self.a_sock_addr}')
        self.a_sock_conn.send(bytes(concat_alice, 'utf-8'))
        self.a_sock_conn.close()

        self.b_sock_conn, self.b_sock_addr = self.ti_sock.accept()
        print(f'Bob has connected from {self.a_sock_addr}')
        self.b_sock_conn.send(bytes(concat_bob, 'utf-8'))
        self.b_sock_conn.close()

        self.ti_sock.close()

IP = socket.gethostname()
PORT = 1234

x = input("Enter x: ")
y = input("Enter y: ")
x = int(x)
y = int(y)

server = Server(IP, PORT)
server.generate(x, y)