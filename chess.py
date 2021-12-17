import functools
from os import error
from os.path import exists
import xml.etree.ElementTree as ET
import re
from contextlib import contextmanager
import json

class Logged( type ):
    """A metaclass that casuses classes that it creates to log their function calls. [Professional Python: Sneeringer]"""
    def __new__( cls, name, bases, attrs ):
        for key, value in attrs.items():
            if callable( value ):
                attrs[ key ] = cls.log_call( value )
        return super( Logged, cls ).__new__( cls, name, bases, attrs )
    
    @staticmethod
    def log_call( func ):
        """Given a function, wrap it with some logging code and return the wrapped function
        [Professional Python: Sneeringer]"""
        def inner( *args, **kwargs ):
            # print( 'function %s was called with arguments %r and '
            #         'keyword arguments %r.' % (func.__name__, args, kwargs ) )
            # print( 'function %s was called with arguments  and '
            #     'keyword arguments.' % func.__name__ )
            
            try:
                response = func( *args, **kwargs )
                # print( 'The function calls to %s was successful' % func.__name__ )
                return response
            except Exception as exc:
                    print( 'The function call to %s raised an exception: %r' % (func.__name__, exc ) )
                    raise
        return inner


def log_move(func):
    @functools.wraps( func )
    def inner( *args, **kwargs ):
        result = func( *args, **kwargs )
        print( Piece.pos2alpha( result ) )
        return result
    return inner

class Chess( metaclass=Logged ):
    allowable_moves_file = ''
    piece_models = ''
    board_model = ''

    pieces = []

    def __init__( self, cs = [], moves_list='', piece_models='', board_model='' ):
        if not cs is None:
            if cs.__str__ == "Chess":
                self.__dict__.update( cs.__dict__ )
                pass
        if exists( moves_list ):
            self.allowable_moves_file = moves_list
        else:
            print( "Moves List: %s not found" % moves_list )
        if exists( piece_models ):
            self.piece_models = piece_models
        if exists( board_model ):
            self.board_model = board_model
        
    def __str__( self ):
        return "Chess"

    def add_piece( self, piece, color, location=9 ):
        pc_factory = piece()
        pc = pc_factory( color, location )
        self.pieces.append( pc )

    def pieceAtRankFile( self, _rank, _file ):
        # bad method, but it works
        for pc in self.pieces:
            rank, file = pc.pos2rankFile( pc._location )
            if( rank == _rank and file == _file ):
                return pc

        return -1

    def dump_pieces( self ):
        board_status = {}
        board_status[ 'whitePawn' ] = []
        board_status[ 'blackPawn' ] = []
        board_status[ 'whiteRook' ] = []
        board_status[ 'blackRook' ] = []
        board_status[ 'whiteBishop' ] = []
        board_status[ 'blackBishop' ] = []
        board_status[ 'whiteKnight' ] = []
        board_status[ 'blackKnight' ] = []
        board_status[ 'whiteQueen' ] = []
        board_status[ 'blackQueen' ] = []
        board_status[ 'whiteKing' ] = []
        board_status[ 'blackKing' ] = []

        for pc in self.pieces:
            if( pc.__str__() == "Pawn[White]" ):
                board_status[ 'whitePawn' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Pawn[Black]" ):
                board_status[ 'blackPawn' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Rook[White]" ):
                board_status[ 'whiteRook' ].append( pc.pos2rankFile( pc._location ) ) 
            elif( pc.__str__() == "Rook[Black]" ):
                board_status[ 'blackRook' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Bishop[White]" ):
                board_status[ 'whiteBishop' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Bishop[Black]" ):
                board_status[ 'blackBishop' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Knight[White]" ):
                board_status[ 'whiteKnight' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Knight[Black]" ):
                board_status[ 'blackKnight' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Queen[White]" ):
                board_status[ 'whiteQueen' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "Queen[Black]" ):
                board_status[ 'blackQueen' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "King[White]" ):
                board_status[ 'whiteKing' ].append( pc.pos2rankFile( pc._location ) )
            elif( pc.__str__() == "King[Black]" ):
                board_status[ 'blackKing' ].append( pc.pos2rankFile( pc._location ) )

        return board_status

class Board():
    num_ranks = 8
    num_files = 8

    def __init__( self, parent ):
        # load board configuration
        tree = ET.parse( "board_setup.xml" ) # fix this to reference Chess object
        root = tree.getroot()

        for child in root:
            if child.tag == "Color":
                for grandchild in child:
                    if grandchild.attrib['type'] == "Pawn":
                        gen = pawn_factory
                    elif grandchild.attrib['type'] == "Rook":
                        gen = rook_factory
                    elif grandchild.attrib['type'] == "Bishop":
                        gen = bishop_factory
                    elif grandchild.attrib['type'] == "Knight":
                        gen = knight_factory
                    elif grandchild.attrib['type'] == "Queen":
                        gen = queen_factory
                    elif grandchild.attrib['type'] == "King":
                        gen = king_factory
                    if grandchild.tag == "Piece":
                        for great_grandchild in grandchild:
                            if great_grandchild.tag == "position":
                                parent.add_piece( gen, child.attrib['type'], Piece.alpha2pos( great_grandchild.text ) )
                                # print( great_grandchild )

    @staticmethod
    def on_board( pos ):
        rank, file = Piece.pos2rankFile( pos )
        if( rank > Board.num_ranks or rank < 1 or file > Board.num_files or file < 1 ):
            return False
        return True

#TODO::Add check and checkmate detection

class Piece():
    _color = []
    _location = []
    allowable_moves_list = []
    _action_count = 0

    def __init__(self, color, location=((1<<3) | 1) ) -> None:
        self._color = color
        self._location = location 
        self.allowable_moves_list = self.load_allowable_moves_list()

    def legal_move_list_generator( self ) -> list:
        return []

    def legal_move( self, new_pos ) -> bool:
        legal_move_list = self.legal_move_list_generator()
        if new_pos in legal_move_list:
            return True
        else:
            return False

    @log_move
    def move( self, new_pos ):
        if not self.legal_move( new_pos ):
            return -1
        self._location = new_pos;
        self._action_count += 1
        return self._location

    @staticmethod
    def pos2alpha( pos ):
        if not Board.on_board( pos ):
            return 'n99'
        curr_row = pos & (0b1111)
        curr_file = pos >> 4

        return '%c%d' % ( chr(curr_file+96), curr_row )

    @staticmethod
    def alpha2pos( pos ) -> int:
        curr_file = ord( pos[0] )
        curr_row = int( pos[1] )

        return ( ((curr_file-96)<<4) | curr_row )

    def load_allowable_moves_list( self ):
        tree = ET.parse( "moves_list.xml" ) # fix this to reference Chess object
        root = tree.getroot()
        
        pc_type = re.search( '^[^\\[]+', self.__str__() )[0]

        moves = []
        for child in root:
            if child.tag == "Piece":
                if type( child.attrib ) is dict:
                    if child.attrib['type'] == pc_type:
                        for grandchild in child:
                            if grandchild.tag == 'move':
                                moves.append( grandchild.text )
        return moves

    @staticmethod
    def get_curr_row( pos ):
        return pos & (0b1111)

    @staticmethod
    def get_curr_file( pos ):
        return pos >> 4

    @staticmethod
    def pos2rankFile( pos ):
        return ( Piece.get_curr_row( pos ), Piece.get_curr_file( pos ) )

    @staticmethod
    def rankFile2pos( row, file ):
        return ( ((file) << 4) | row )

    #TODO::-> Finish 't' flag to check for enemies
    #      -> Add collision detection to all entries
    #      -> Add diagonal selection
    #      -> Add castling
    def legal_move_list_generator( self ) -> list:
        curr_row = Piece.get_curr_row( self._location )
        curr_file = Piece.get_curr_file( self._location )

        allowable_list = []
        for moves in self.allowable_moves_list:
            # convert each move into an action
            res = re.split( ',|:', moves )
            if len( res ) < 2:
                raise Exception( "Illegal move definition: %s" % moves )
            
            row_update = int( res[0] )
            file_update = int( res[1] )

            pos = Piece.rankFile2pos( curr_row + row_update, curr_file + file_update )

            if not Board.on_board( Piece.rankFile2pos( curr_row + row_update, curr_file + file_update ) ):
                continue

            appendables = []

            if len( res ) == 3:
                flags = res[2]

                if( flags == 'i' ):
                    if self._action_count == 0:
                            appendables.append( pos )
                elif( flags == 't' ):
                    # option for taking
                    pass
                elif( flags == 'r' ):
                    if( row_update > 0 ):
                        for i in range( curr_row, Board.num_files+1 ):
                            appendables.append( Piece.rankFile2pos( curr_row + i, curr_file) )
                    elif( row_update < 0 ):
                        for i in range( curr_row, 1, -1 ):
                            appendables.append( Piece.rankFile2pos( curr_row + i, curr_file) )
                elif( flags == 'f' ):
                    if( file_update > 0 ):
                        for i in range( curr_file, Board.num_files+1 ):
                            appendables.append( Piece.rankFile2pos( curr_row, curr_file + i) )
                    elif( file_update < 0 ):
                        for i in range( curr_file, 1, -1 ):
                            appendables.append( Piece.rankFile2pos( curr_row, curr_file + i) )
                elif( flags == 'd' ):
                    # option for extended diagonal motion
                    pass
                elif( flags == 'c' ):
                    # special flag for castling
                    pass
                else:
                    appendables.append( pos )
            else:
                appendables.append( pos )

            allowable_list += appendables            
            # if append:
            #     allowable_list.append( Piece.rankFile2pos( curr_row + row_update, curr_file + file_update ) )
 
        return allowable_list

def pawn_factory():
    class Pawn( Piece ):
        def __repr__(self):
            return 'Pawn[%s]' % self._color
        
        def __str__( self ):
            return 'Pawn[%s]' % self._color

    return Pawn

def rook_factory():
    class Rook( Piece ):
        def __repr__(self):
            return 'Rook[%s]' % self._color
        
        def __str__( self ):
            return 'Rook[%s]' % self._color

    return Rook

def bishop_factory():
    class Bishop( Piece ):
        def __repr__(self):
            return 'Bishop[%s]' % self._color
        
        def __str__( self ):
            return 'Bishop[%s]' % self._color

    return Bishop

def knight_factory():
    class Knight( Piece ):
        def __repr__(self):
            return 'Knight[%s]' % self._color
        
        def __str__( self ):
            return 'Knight[%s]' % self._color

    return Knight

def queen_factory():
    class Queen( Piece ):
        def __repr__(self):
            return 'Queen[%s]' % self._color
        
        def __str__( self ):
            return 'Queen[%s]' % self._color

    return Queen

def king_factory():
    class King( Piece ):
        def __repr__(self):
            return 'King[%s]' % self._color
        
        def __str__( self ):
            return 'King[%s]' % self._color

    return King

if __name__ == "__main__":
    cs = Chess( moves_list='moves_list.xml' )

    b = Board( cs )
    
    # cs.pieces[8].move( )
    print( cs.pieces[0].__str__() )

    # cs.pieces[0].move( Piece.alpha2pos( 'a7' ) ) 

    i = Piece.alpha2pos( 'a8' )
    print( i )
    print( Piece.pos2rankFile( i ) )
    print( Piece.pos2rankFile( 10 ) )

    print( json.dumps( cs.dump_pieces() ) )