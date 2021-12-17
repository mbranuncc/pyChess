import asyncore
import json

from configparser import ConfigParser

# personal imports
import api
from chess import Chess
from chess import Board
from chess import Piece

capi = api.ChessAPI( 'localhost', 8081 )
capiMessage = capi.ChessMessageHandler()

cs = Chess( moves_list = 'moves_list.xml' )
b = Board( cs )

def board_init_cb( reply ):
    v = cs.dump_pieces()
    v[ 'type' ] = "INIT_RESPONSE"
    return json.dumps( v )

def available_moves_cb( reply ):
    # get piece position
    rank = reply[ 'rank' ]
    file = reply[ 'file' ]
    pc = cs.pieceAtRankFile( rank, file )

    msg = {}
    msg[ 'type' ] = "AVAILABLE_MOVES_RESPONSE"
    if( pc == -1 ):
        print( "NO PIECE AT LOCATION" )
        msg[ 'error' ] = "NO PIECE AT LOCATION"
        return json.dumps( msg )
    msg['piece'] = pc.__str__()
    moves = pc.legal_move_list_generator()
    msg[ 'moves' ] = [ Piece.pos2rankFile( e ) for e in moves ]
    return json.dumps( msg )

def current_board_cb( reply ):
    v = cs.dump_pieces()
    v[ 'type' ] = "CURRENT_BOARD_RESPONSE"
    return json.dumps( v )

def move_request_cb( reply ):
    msg = {}
    msg['type'] = "MOVE_RESPONSE"
    # find piece
    pc_rank = reply['start_rank']
    pc_file = reply['start_file']
    pc = cs.pieceAtRankFile( pc_rank, pc_file )
    if( pc == -1 ):
        msg['error'] = "NO PIECE AT STARTING LOCATION"
        return json.dumps( msg )
    
    # check to see if the desired move is legal
    new_rank = reply['end_rank']
    new_file = reply['end_file']
    new_pos = pc.rankFile2pos( new_rank, new_file )
    status = pc.move( new_pos )
    if( status != -1 ):
        msg['status'] = 1
    else:
        msg['status'] = 0
    return json.dumps( msg )

capiMessage.registerCallback( "INIT_REQUEST", board_init_cb )
capiMessage.registerCallback( "AVAILABLE_MOVES_REQUEST", available_moves_cb )
capiMessage.registerCallback( "CURRENT_BOARD_REQUEST", current_board_cb )
capiMessage.registerCallback( "MOVE_REQUEST", move_request_cb )

class ClientHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        data = self.recv(8192)
        if data:
            v = json.loads( data )
            ret = capiMessage.distribute( v )
            self.send( bytes( ret, 'ascii' ) )

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

if( __name__ == "__main__" ):
    config = ConfigParser()

    config.read( 'chess_config.ini' )
    
    server = ChessServer(config.get( 'network', 'host' ), int(config.getfloat( 'network', 'port' ) ) )
    asyncore.loop()