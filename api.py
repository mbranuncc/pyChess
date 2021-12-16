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
        asyncore.loop()
        return msg.reply

    class ChessMessageHandler():
        
        class Request( Enum ):
            INIT = 1
            AVAILABLE_MOVES = 2
            CURRENT_BOARD = 3

        @staticmethod
        def generator( request_type, *args):
            msg = {}
            if( request_type == ChessAPI.ChessMessageHandler.Request.INIT ):
                if( len( args ) != 0 ):
                    print( "INIT takes no arguments" )
                    msg[ 'error' ] = "INIT takes no arguments"
                    return msg  
                msg[ 'action' ] = "INIT"
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.AVAILABLE_MOVES ):
                if( len( args ) != 2 ):
                    print( "AVAILABLE_MOVES takes 2 arguments")
                    msg[ 'error' ] = "AVAILABLE_MOVES takes 2 arguments"
                    return msg
                msg[ 'action' ] = "AVAILABLE_MOVES"
                msg[ 'file' ] = args[0][0]
                msg[ 'rank' ] = args[0][1]
                return msg
            elif( request_type == ChessAPI.ChessMessageHandler.Request.CURRENT_BOARD ):
                if( len( args ) != 0 ):
                    print( "CURRENT_BOARD takes no arguments" )
                    msg[ 'error' ] = "CURRENT_BOARD takes no arguments"
                    return msg
                return msg

        def parse( reply ):
            pass



c = ChessAPI( 'localhost', 8081 )
msg = c.ChessMessageHandler.generator( c.ChessMessageHandler.Request.INIT )
reply = c.send_message( msg )
print( "PRINTING REPLY" )
print( reply )
            
