import socket
import threading

class Player:
    MOD_CONST = 16384

    def __init__(self):
        """
        Initialize Player class which instantiates a socket with IPv4 address family and TCP socket type.
        This socket becomes a data member of this Player class.
        """
        self.player_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_server(self, ip, port, is_closed=False):
        """
        Connects this Player class to a server socket which provides shares of [a], [b], [c] (randomly generated secret 
        shared values) to the Player class and assigned as data members.
        """
        # If socket has already been used and was previously closed, create new socket
        if (is_closed):
            generate_new_socket()

        self.player_sock.connect((ip, port))
        data = self.player_sock.recv(1024).decode('utf-8')
        split_data = data.split(':')
        self.share_a = int(split_data[0])
        self.share_b = int(split_data[1])
        self.share_c = int(split_data[2])
        self.share_x = int(split_data[3])
        self.share_y = int(split_data[4])
        self.player_sock.close()

        # Do local computations
        self.share_d = (self.share_x - self.share_a) % self.MOD_CONST
        self.share_e = (self.share_y - self.share_b) % self.MOD_CONST
        print(f'My shares: {self.share_a}, {self.share_b}, {self.share_c}, {self.share_x}, {self.share_y}')

    def setup_communication(self, ip, port, is_closed=False):
        """
        Set up server to communicate with other Player. 
        """
        if (is_closed):
            self.generate_new_socket()

        self.player_sock.bind((ip, port))
        self.player_sock.listen(5)
        self.player_sock.settimeout(10)

        self.send_local_computations()

        self.player_sock.close()
    
    def send_local_computations(self):
        """
        We want each player to have the other parties local computations of d_alice, e_alice, d_bob, e_bob to compute z_alice and 
        z_bob where z = x * y.
        """
        concat_d_e = f'{self.share_d}:{self.share_e}'
        player_conn, player_addr = self.player_sock.accept()
        player_conn.send(bytes(concat_d_e, 'utf-8'))
        print(f'I have sent my local computations of d = {self.share_d} and e = {self.share_e}!')

    def get_player_info(self, ip, port, is_closed=False, use_d_times_e=True):
        """
        This method makes it so a player can communicate with another player. Mainly to share their local computations of player_d and player_e. 
        Then this Party will compute d = d_other_party + d_my_party and e = e_other_party + e_my_party. Finally we obtain a share of z for this party
        """
        if (is_closed):
            self.generate_new_socket()
        
        self.player_sock.connect((ip, port))
        data = self.player_sock.recv(1024).decode('utf-8')
        split_data = data.split(':')
        self.other_player_d = int(split_data[0])
        self.other_player_e = int(split_data[1])
        print(f'I have received the other parties local computations of d = {self.other_player_d} and e = {self.other_player_e}')
        self.player_sock.close()

        self.d = (self.other_player_d + self.share_d) % self.MOD_CONST
        self.e = (self.other_player_e + self.share_e) % self.MOD_CONST
        print(f'Using the other parties local computations to get d = {self.d} and e = {self.e}')

        if (use_d_times_e):
            self.share_z = ((self.d * self.share_b) + (self.e * self.share_a) + self.share_c + (self.d * self.e)) % self.MOD_CONST
        else:
            self.share_z = ((self.d * self.share_b) + (self.e * self.share_a) + self.share_c) % self.MOD_CONST
        print(f'My share of z is {self.share_z}')

    def generate_new_socket(self):
        """
        This generates a new socket object to the player_sock data member if it was previously closed
        """
        self.player_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
# Communicate with TI/Server
IP = socket.gethostname()
PORT = 1234
alice = Player()
alice.connect_server(IP, PORT, False)
bob = Player()
bob.connect_server(IP, PORT, False)
#print(f'Alice\'s shares: {alice.share_a}, {alice.share_b}, {alice.share_c}, {alice.share_x}, {alice.share_y}')
#print(f'Bob\'s shares: {bob.share_a}, {bob.share_b}, {bob.share_c}, {bob.share_x}, {bob.share_y}')

PORT = 12345
# Alice sets up a server socket for communication between players (Alice and Bob) and send Bob her local computations
t1 = threading.Thread(target=alice.setup_communication, kwargs={'ip':IP, 'port':PORT, 'is_closed':True})
# Bob gets input sent from the server socket Alice creates inorder to send her local computations to him
t2 = threading.Thread(target=bob.get_player_info, kwargs={'ip': IP, 'port': PORT, 'is_closed':True, 'use_d_times_e':False})
t1.start()
t2.start()
t1.join()
t2.join()

PORT = 12346
# Bob sets up a server socket for communication between players (Alice and Bob) and send Alice his local computations
t3 = threading.Thread(target=bob.setup_communication, kwargs={'ip':IP, 'port':PORT, 'is_closed':True})
# Alice gets input sent from the server socket Bob creates inorder to send his local computations to her
t4 = threading.Thread(target=alice.get_player_info, kwargs={'ip': IP, 'port': PORT, 'is_closed':True, 'use_d_times_e':True})
t3.start()
t4.start()
t3.join()
t4.join()
print(f'Result = {(alice.share_z + bob.share_z) % 16384}')