import asyncore
import json

from configparser import ConfigParser

class ClientHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.send(data)
            v = json.loads( data )
            print( v['action'] )

    def handle_close( self ):
        print( "Disconnecting..." )
        self.close()

class ChessServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        handler = ClientHandler(sock)

server = ChessServer('localhost', 8081)
asyncore.loop()