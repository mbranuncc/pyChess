import asyncore
import json
from enum import Enum

from chess import Chess

class ChessAPI():
    host = []
    port = []

    def __init__( self, _host, _port ):
        self.host = _host
        self.port = _port

    class ChessASYNC(asyncore.dispatcher):
        message = []
        reply = []

        def __init__(self, host, port, _message):
            asyncore.dispatcher.__init__(self)
            self.create_socket()
            self.connect( (host, port) )

            if not isinstance( _message, dict ):
                print( "Message must be in json format" )

            self.message = bytes( json.dumps( _message ), 'ascii' )

        def handle_connect(self):
            pass

        def handle_close(self):
            self.close()

        def handle_read(self):
            v = self.recv( 8192 )
            self.reply = v

            self.handle_close()

        def writable(self):
            return (len(self.message) > 0)

        def handle_write(self):
            sent = self.send(self.message)
            self.message = self.message[sent:]

    def send_message( self, message ):
        msg = self.ChessASYNC( self.host, self.port, message )
        asyncore.loop( timeout=1 )
        return msg.reply

    class ChessMessageHandler():

        callbacks = {}
        
        class Request( Enum ):
            INIT_REQUEST = 1
            INIT_RESPONSE = 2
            AVAILABLE_MOVES_REQUEST = 3
            AVAILABLE_MOVES_RESPONSE = 4
            CURRENT_BOARD_REQUEST = 5
            CURRENT_BOARD_RESPONSE = 6
            MOVE_REQUEST = 7
            MOVE_RESPONSE = 8

        @staticmethod
        def generator( request_type, *args):
            msg = {}
            if( request_type == ChessAPI.ChessMessageHandler.Request.INIT_REQUEST ):
                if( len( args ) != 0 ):
                    print( "INIT_REQUEST takes no arguments" )
                    msg[ 'type' ] = "INIT_REQUEST"
                    msg[ 'error' ] = "INIT_REQUEST takes no arguments"
                    return msg  
                msg[ 'type' ] = "INIT_REQUEST"
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.INIT_RESPONSE ):
                if( len( args ) != 1 ):
                    print( "INIT_RESPONSE takes 1 arguments" )
                    msg[ 'type' ] = "INIT_RESPONSE"
                    msg[ 'error' ] = "INIT_RESPONSE takes 1 arguments"
                    return msg
                msg[ 'type' ] == "INIT_RESPONSE"
                msg[ 'init' ] = args[0]
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.AVAILABLE_MOVES_REQUEST ):
                if( len( args ) != 2 ):
                    print( "AVAILABLE_MOVES_REQUEST takes 2 arguments")
                    msg[ 'type' ] = "AVAILABLE_MOVES_REQUEST"
                    msg[ 'error' ] = "AVAILABLE_MOVES_REQUEST takes 2 arguments"
                    return msg
                msg[ 'type' ] = "AVAILABLE_MOVES_REQUEST"
                msg[ 'rank' ] = args[0]
                msg[ 'file' ] = args[1]
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.AVAILABLE_MOVES_RESPONSE ):
                if( len( args ) != 1 ):
                    print( "AVAILABLE_MOVES_RESPONSE takes 1 argument" )
                    msg[ 'type' ] = "AVAILABLE_MOVES_RESPONSE"
                    msg[ 'error' ] = "AVAILABLE_MOVES_RESPONSE takes 1 argument"
                    return msg
                msg[ 'type' ] = "AVAILABLE_MOVES_RESPONSE"
                msg[ 'moves' ] = args[0]
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.CURRENT_BOARD_REQUEST ):
                if( len( args ) != 0 ):
                    print( "CURRENT_BOARD takes no arguments" )
                    msg[ 'error' ] = "CURRENT_BOARD takes no arguments"
                    return msg
                msg[ 'type' ] = "CURRENT_BOARD"
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.MOVE_REQUEST ):
                msg['type'] = "MOVE_REQUEST"
                if( len( args ) != 4 ):
                    print( "MOVE_REQUEST takes 4 arguments" )
                    msg['error'] = "MOVE_REQUEST takes 4 arguments"
                    return msg
                msg['start_rank'] = args[0]
                msg['start_file'] = args[1]
                msg['end_rank'] = args[2]
                msg['end_file'] = args[3]
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.MOVE_RESPONSE ):
                msg['type'] = "MOVE_RESPONSE"
                if( len( args ) != 1 ):
                    print( "MOVE_RESPONSE takes 1 argument" )
                    msg['error'] = "MOVE_RESPONSE takes 1 arguments"
                    return msg
                msg['status'] = args[0]
                return msg

        def distribute( self, reply ):
            otpt = ""
            if( reply[ 'type' ] == "INIT_REQUEST" ):
                try:
                    otpt = self.callbacks[ "INIT_REQUEST" ]( reply )
                except:
                    pass
            elif( reply[ 'type' ] == "INIT_RESPONSE" ):
                try:
                    otpt = self.callbacks[ "INIT_RESPONSE" ]( reply )
                except:
                    pass
            elif( reply[ 'type' ] == "AVAILABLE_MOVES_REQUEST" ):
                # try:
                    otpt = self.callbacks[ "AVAILABLE_MOVES_REQUEST" ]( reply )
                # except:
                    # pass
            elif( reply[ 'type' ] == "AVAILABLE_MOVES_RESPONSE" ):
                try:
                    otpt = self.callbacks[ "AVAILABLE_MOVES_RESPONSE" ]
                except:
                    pass
            elif( reply[ 'type' ] == "CURRENT_BOARD_REQUEST" ):
                try:
                    otpt = self.callbacks[ "CURRENT_BOARD_REQUEST" ]( reply )
                except:
                    pass
            elif( reply[ 'type' ] == "CURRENT_BOARD_RESPONSE" ):
                try:
                    otpt = self.callbacks[ "CURRENT_BOARD_RESPONSE" ]( reply )
                except:
                    pass
            elif( reply[ 'type' ] == "BOARD_CONFIG_REQUEST" ):
                try:
                    otpt = self.callbacks[ "BOARD_CONFIG_REQUEST" ]( reply )
                except:
                    pass
            elif( reply[ 'type' ] == "BOARD_CONFIG_RESPONSE" ):
                try:
                    otpt = self.callbacks[ "BOARD_CONFIG_RESPONSE" ]( reply )
                except:
                    pass
            elif( reply[ 'type' ] == "MOVE_REQUEST" ):
                # try:
                    otpt = self.callbacks[ "MOVE_REQUEST" ]( reply )
                # except:
                #     pass
            elif( reply[ 'type' ] == "MOVE_RESPONSE" ):
                try:
                    otpt = self.callbacks[ "MOVE_RESPONSE" ]( reply )
                except:
                    pass
            else:
                print( "Reply type not found" )

            return otpt

        def registerCallback( self, tag, function ):
            self.callbacks[ tag ] = function


if( __name__ == "__main__" ):
    c = ChessAPI( 'localhost', 8081 )
    msg = c.ChessMessageHandler.generator( c.ChessMessageHandler.Request.INIT_REQUEST )
    reply = c.send_message( msg )
    print( reply )

    msg = c.ChessMessageHandler.generator( c.ChessMessageHandler.Request.AVAILABLE_MOVES_REQUEST, 2, 1 )
    reply = c.send_message( msg )
    print( reply )
            
