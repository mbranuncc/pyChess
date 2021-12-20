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
        print( args[0].pos2alpha( result ) )
        return result
    return inner

class Chess( metaclass=Logged ):
    allowable_moves_file = ''
    piece_models = ''
    board_model = ''

    pieces = []
    graveyard = []
    board = []

    game_state = [] # OPEN, BLACK_CHECK, WHITE_CHECK, BLACK_CHECKMATE, WHITE_CHECKMATE
    turn = [] # WHITE, BLACK

    def __init__( self, cs = [], moves_list='', piece_models='', board_model='' ):
        self.game_state = "OPEN"
        self.turn = "WHITE"
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
        pc = pc_factory( self, color, location )
        self.pieces.append( pc )

    def pieceAtRankFile( self, _rank, _file ):
        # bad method, but it works
        for pc in self.pieces:
            rank, file = pc.pos2rankFile( pc._location )
            if( rank == _rank and file == _file ):
                return pc

        return -1

    def registerBoard( self, b ):
        self.board = b

    def returnPiecefromGraveyard( self, target_pc ):
        if( len( self.graveyard ) < 1 ):
            return
        for pc in reversed( self.graveyard ):
            if( target_pc._location == pc._location ):
                self.graveyard.remove( pc )
                self.pieces.append( pc )
                break
        pass

    def sendPieceToGraveyard( self, target_pc ):
        t_rank, t_file = target_pc.pos2rankFile( target_pc._location )
        for pc in self.pieces:
            rank, file = pc.pos2rankFile( pc._location )
            if( t_rank == rank and t_file == file ):
                self.pieces.remove( pc )
                self.graveyard.append( pc )
        pass

    def verifyGameIntegrity( self ):
        # to be run at the end of each loop to perform mundane tasks to ensure
        # that everything is how it should be i.e.
        # -> both kings exist
        # -> both teams have non-zero number of pieces
        # -> (maybe) both kings aren't in check(mate)
        curr_turn = self.turn

        whiteKing = self.getPiecesByName( "King[White]" )
        assert( whiteKing != -1 )
        checkers = self.inCheck( whiteKing[0] )
        assert( checkers != -1 )
        if( len( checkers ) > 0 ):
            print( "White King in check" )
            if( self.inCheckmate( whiteKing[0] ) ):
                print( "White in Checkmate" )

        blackKing = self.getPiecesByName( "King[Black]" )
        assert( blackKing != -1 )
        checkers = self.inCheck( blackKing[0] )
        assert( checkers != -1 )
        if( len( checkers ) > 0 ):
            print( "Black King in check" )
            # check if it is checkmate
            if( self.inCheckmate( blackKing[0] ) ):
                print( "Black in Checkmate" )

        self.turn = curr_turn
        pass

    def getPiecesByColor( self, color: str ):
        piece_list = []
        for pc in self.pieces:
            if( pc._color.upper() == color.upper() ):
                piece_list.append( pc )
        return piece_list

    def getPiecesByName( self, name: str ):
        piece_list = []
        for pc in self.pieces:
            if( pc.__str__().upper() == name.upper() ):
                piece_list.append( pc )
            pass
        return piece_list

    def inCheckmate( self, king ):
        # this is going to be much harder than check...
        # need to loop through every piece on king's team and
        # see if any piece has available moves.
        # if no pieces on the kings team have any moves, then its checkmate

        # get all the pieces on the kings team
        c_pieces = self.getPiecesByColor( king._color )

        for pc in c_pieces:
            moves = pc.legal_move_list_generator()
            if( len( moves ) > 0 ):
                return 0
        return 1
            
    def inCheck( self, king ):
        # is the piece actually a king?
        if not "King" in king.__str__():
            return -1

        # proposed algorithm for verifying check
        # 1. search ranks, files and diagonals up to next piece
        # 2. check if piece is enemy and if enemy can move in a way to create check
        # 3. check for knight moves (TODO)
        searchSpaces = {}
        searchSpaces[ 'rightRank' ] = [ 0, +1 ]
        searchSpaces[ 'leftRank' ] = [ 0, -1 ]
        searchSpaces[ 'downFile' ] = [ +1, 0 ]
        searchSpaces[ 'upFile' ] = [ -1, 0  ]
        searchSpaces[ 'upRight' ] = [ +1, +1 ]
        searchSpaces[ 'upLeft' ] = [ -1, +1 ]
        searchSpaces[ 'downLeft' ] = [ -1, -1 ]
        searchSpaces[ 'downRight' ] = [ +1, -1 ]

        checkers = []

        for key in searchSpaces:
            # reset origin
            tmp_rank, tmp_file = Piece.pos2rankFile( king._location )
            tmp_rank += searchSpaces[ key ][0]
            tmp_file += searchSpaces[ key ][1]
            # find next piece along direction or edge of board
            while( tmp_rank in range( 1, self.board.num_ranks+1 ) and\
                    tmp_file in range( 1, self.board.num_files+1 ) ):
                pc = self.pieceAtRankFile( tmp_rank, tmp_file )
                if( pc != -1 and pc._color != king._color ):
                    # a piece has been found along this line, check if it is dangerous
                    # this is done by generating its list of allowable moves
                    # and see if the King's square is one of those moves
                    self.turn = pc._color.upper() # wow this is bad
                    allowable_moves = pc.legal_move_list_generator()
                    self.turn = king._color.upper()
                    if( king._location in allowable_moves ):
                        # target acquired
                        checkers.append( pc )
                        break
                    pass
                elif( pc != -1 and pc._color == king._color ):
                    break

                tmp_rank += searchSpaces[ key ][0]
                tmp_file += searchSpaces[ key ][1]
                pass
            pass
        return checkers

    def finishTurn( self ):
        self.verifyGameIntegrity()

        if( self.turn == "WHITE" ):
            self.turn = "BLACK"
        elif( self.turn == "BLACK" ):
            self.turn = "WHITE"
        else:
            print( "Turn switch error" )
            assert( 1 == 0 )

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
        parent.registerBoard( self )

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

    def on_board( self, pos ):
        rank, file = Piece.pos2rankFile( pos )
        if( rank > self.num_ranks or rank < 1 or file > self.num_files or file < 1 ):
            return False
        return True

class Piece():
    _color = []
    _location = []
    allowable_moves_list = []
    _action_count = 0

    parent = []

    def __init__(self, parent, color, location=((1<<3) | 1) ) -> None:
        self._color = color
        self._location = location 
        self.allowable_moves_list = self.load_allowable_moves_list()
        self.parent = parent

    def legal_move_list_generator( self ) -> list:
        return []

    def legal_move( self, new_pos ) -> bool:
        legal_move_list = self.legal_move_list_generator()
        if new_pos in legal_move_list:
            return True
        else:
            return False

    def simulateMove( self, new_pos, func, args ):
        # removed due to recursion issues when creating list of available
        # moves, not a good design

        # if not self.legal_move( new_pos ):
        #     return -2

        # save position to return after function call
        curr_pos = self._location

        # check if this move results in a taken piece
        e_rank, e_file = Piece.pos2rankFile( new_pos )
        enemy_pc = self.parent.pieceAtRankFile( e_rank, e_file )
        if( enemy_pc != -1 ):
            # verify that a mistake wasn't made and the piece is occupied by friendly
            if( enemy_pc._color == self._color ):
                return -1

            self.parent.sendPieceToGraveyard( enemy_pc ) 

        self._location = new_pos

        # this is where the function can be called to evaluate something
        # after a particular move

        otpt = func( *args )

        # return everything to the way it was
        self._location = curr_pos
        if( enemy_pc != -1 ):
            if( enemy_pc._color != self._color ):
                self.parent.returnPiecefromGraveyard( enemy_pc ) 
        
        return otpt

    @log_move
    def move( self, new_pos ):
        if not self.legal_move( new_pos ):
            return -1

        # check if this move results in a taken piece
        e_rank, e_file = Piece.pos2rankFile( new_pos )
        enemy_pc = self.parent.pieceAtRankFile( e_rank, e_file )
        if( enemy_pc != -1 ):
            # verify that a mistake wasn't made and the piece is occupied by friendly
            if( enemy_pc._color == self._color ):
                return -1

            self.parent.sendPieceToGraveyard( enemy_pc ) 

        self._location = new_pos
        self._action_count += 1

        self.parent.finishTurn()

        return self._location

    def pos2alpha( self, pos ):
        if not self.parent.board.on_board( pos ):
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

    #TODO
    #      -> Add castling
    #      -> Check if check or checkmate are applicable
    def legal_move_list_generator( self ) -> list:
        if( self._color.upper() != self.parent.turn.upper() ):
            return []

        curr_row = Piece.get_curr_row( self._location )
        curr_file = Piece.get_curr_file( self._location )

        # need the king associated with piece color to ensure that 
        # move wouldn't endanger the respective king
        if( self._color.upper() == "WHITE" ):
            king = self.parent.getPiecesByName( "King[White]" )
        elif( self._color.upper() == "BLACK" ):
            king = self.parent.getPiecesByName( "King[Black]" )
        assert( king != -1 )

        allowable_list = []
        for moves in self.allowable_moves_list:
            # convert each move into an action
            res = re.split( ',|:', moves )
            if len( res ) < 2:
                raise Exception( "Illegal move definition: %s" % moves )
            
            row_update = int( res[0] )
            file_update = int( res[1] )
            if( row_update == 0 and file_update == 0 ):
                continue

            if( self._color == "Black" ):
                row_update = row_update * -1
                file_update = file_update * -1

            pos = Piece.rankFile2pos( curr_row + row_update, curr_file + file_update )

            if not self.parent.board.on_board( pos ):
                continue

            appendables = []

            if len( res ) == 3:
                flags = res[2]

                if( flags == 'i' ):
                    tmp_row = curr_row + row_update
                    tmp_file = curr_file + file_update
                    if self._action_count == 0:
                        pc = self.parent.pieceAtRankFile( tmp_row, tmp_file )
                        if( pc == -1 ):
                            # simulate move to see if it results in check
                            outcome = self.simulateMove( Piece.rankFile2pos( tmp_row, tmp_file ),\
                                            self.parent.inCheck, king )
                            if not outcome:
                                appendables.append( Piece.rankFile2pos( tmp_row, tmp_file ) )
                elif( flags == 't' ):
                    # option for taking, mostly pawns
                    tmp_row = curr_row + row_update
                    tmp_file = curr_file + file_update

                    # see if there is a piece in this space
                    pc = self.parent.pieceAtRankFile( tmp_row, tmp_file )
                    if( pc != -1 ):
                        # check if this piece is the opposite color of this piece
                        if( self._color != pc._color ):
                            # simulate move to see if it results in check
                            outcome = self.simulateMove( Piece.rankFile2pos( tmp_row, tmp_file ),\
                                            self.parent.inCheck, king )
                            if not outcome:
                                appendables.append( Piece.rankFile2pos( tmp_row, tmp_file ) )
                    pass
                elif( flags == 'r' or flags == 'f' or flags == 'd' ):
                    tmp_row = curr_row + row_update
                    tmp_file = curr_file + file_update
                    # option for extended diagonal motion
                    while( self.pos2alpha( Piece.rankFile2pos( tmp_row, tmp_file ) ) != 'n99' ):
                        pc_at = self.parent.pieceAtRankFile( tmp_row, tmp_file )
                        if( pc_at != -1 and pc_at._color == self._color ):
                            break

                        # simulate move to see if it results in check
                        outcome = self.simulateMove( Piece.rankFile2pos( tmp_row, tmp_file ),\
                                        self.parent.inCheck, king )
                        if not outcome:
                            appendables.append( Piece.rankFile2pos( tmp_row, tmp_file ) )

                        tmp_row += row_update
                        tmp_file += file_update
                        if( pc_at != -1 and pc_at._color != self._color ):
                            break
                    pass
                elif( flags == 'c' ):
                    # special flag for castling
                    pass
                else:
                    print( "Unrecognized flag" )
                    pass
            else:
                tmp_row = curr_row + row_update
                tmp_file = curr_file + file_update
                pc = self.parent.pieceAtRankFile( tmp_row, tmp_file )
                if( pc == -1 or pc._color != self._color ):
                    # simulate move to see if it results in check
                    outcome = self.simulateMove( Piece.rankFile2pos( tmp_row, tmp_file ),\
                                    self.parent.inCheck, king )
                    if not outcome:
                        appendables.append( Piece.rankFile2pos( tmp_row, tmp_file ) )

            allowable_list += appendables            
 
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

    i, j = Piece.pos2rankFile( 81 )
    print( i )
    print( j )
    print( Piece.pos2rankFile( i ) )
    print( Piece.pos2rankFile( 10 ) )
    print( Piece.alpha2pos( 'b4' ) )

    print( json.dumps( cs.dump_pieces() ) )