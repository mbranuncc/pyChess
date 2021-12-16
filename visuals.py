import pyglet
from pyglet.window import mouse
from pyglet import shapes
from pyglet import image
from pyglet.gl import *
from configparser import ConfigParser
from enum import Enum

class Visual():
    window = []
    batch = []

    def __init__( self ):
        self.window = pyglet.window.Window(resizable=True)
        self.batch = pyglet.graphics.Batch()

class VisualBoard( Visual ):
    num_ranks = 0
    num_files = 0
    lightColor = (238,238,210)
    darkColor = (118,150,86)
    highlightColor = (186,202,68)
    baseBorderColor = (0,0,0)
    configFile = 'visual_config.ini'
    num_pieces = 0
    current_focus = [ -1, -1 ]

    piece_selected = -1

    class ChessPiece( Enum ):
        whitePawn = 0
        blackPawn = 1
        whiteRook = 2
        blackRook = 3
        whiteBishop = 4
        blackBishop = 5
        whiteKnight = 6
        blackKnight = 7
        whiteQueen = 8
        blackQueen = 9
        whiteKing = 10
        blackKing = 11


    config = ConfigParser()

    squareAddress = []
    Pieces = {}

    def __init__( self, _num_ranks, _num_files, width, height ):
        super(VisualBoard, self).__init__()
        self.num_ranks = _num_ranks
        self.num_files = _num_files

        squares = VisualBoard.delimitSquares( width, height, self.num_files, self.num_ranks )

        self.squareAddress = self.generateBoardPrimitives( squares )
        self.colorSquares()

        self.config.read( self.configFile )

    def addPiece( self, piece_type, x_loc, y_loc ):
        if( piece_type == self.ChessPiece.whitePawn ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.whitePawn, self.config.get( 'images', 'whitePawn' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.blackPawn ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.blackPawn, self.config.get( 'images', 'blackPawn' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.whiteRook ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.whiteRook, self.config.get( 'images', 'whiteRook' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.blackRook ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.blackRook, self.config.get( 'images', 'blackRook' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.whiteBishop ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.whiteBishop, self.config.get( 'images', 'whiteBishop' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.blackBishop ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.blackBishop, self.config.get( 'images', 'blackBishop' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.whiteKnight ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.whiteKnight, self.config.get( 'images', 'whiteKnight' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.blackKnight ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.blackKnight, self.config.get( 'images', 'blackKnight' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.whiteKing ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.whiteKing, self.config.get( 'images', 'whiteKing' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.blackKing ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.blackKing, self.config.get( 'images', 'blackKing' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.whiteQueen ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.whiteQueen, self.config.get( 'images', 'whiteQueen' ), x_loc, y_loc ]
        elif( piece_type == self.ChessPiece.blackQueen ):
            self.Pieces[ self.num_pieces ] = [ self.ChessPiece.blackQueen, self.config.get( 'images', 'blackQueen' ), x_loc, y_loc ]
        else:
            print( "Could not add piece" )
            return

        self.Pieces[ self.num_pieces ].append( image.load( self.Pieces[ self.num_pieces][1] ) )
        # anchor into center
        self.Pieces[ self.num_pieces ][4].anchor_x = self.Pieces[ self.num_pieces ][4].width // 2
        self.Pieces[ self.num_pieces ][4].anchor_y = self.Pieces[ self.num_pieces ][4].height // 2

        self.num_pieces += 1

    def resizeSquares( self, width, height ):
        boxes = self.delimitSquares( width, height, self.num_files, self.num_ranks )

        ind = 0
        for i in range( 0, self.num_files ):
            for j in range( 0, self.num_ranks ):
                self.getSquare( i, j ).x = boxes[ind][0]
                self.getSquare( i, j ).y = boxes[ind][1]
                self.getSquare( i, j ).width = boxes[ind][2]
                self.getSquare( i, j ).height = boxes[ind][3]
                ind += 1

    def generateBoardPrimitives( self, square_info ):
        Matrix = [[0 for x in range(self.num_files)] for y in range(self.num_ranks)] 
        i = 0
        j = 0
        for square in square_info:
            rec = shapes.BorderedRectangle(x=square[0], y=square[1], width=square[2], height=square[3], border=3, border_color=self.baseBorderColor, batch=self.batch )
            rec.opacity = 250

            Matrix[ i ][ j ] = rec
            i += 1
            if( i == self.num_files ):
                i = 0
                j += 1

        return Matrix

    def colorSquares( self ):
        for i in range( 0, self.num_files ):
            for j in range( 0, self.num_ranks ):
                if( (i+j) % 2 == 0 ):
                    self.getSquare( i, j ).color = self.lightColor
                else:
                    self.getSquare( i, j ).color = self.darkColor

    def getSquare( self, i, j ):
        return self.squareAddress[ i ][ j ]

    def getCoordinateSquare( self, x, y ):
        swidth, sheight = self.window.get_size()
        bwidth = swidth // self.num_files
        bheight = sheight // self.num_ranks

        i = x // bwidth
        j = y // bheight

        return i, j

    def setFocus( self, i, j ):
        self.current_focus = [ i, j ]

    def highlightFocus( self ):
        if( self.current_focus[0] != -1 and self.current_focus[1] != -1 ):
            rec = self.getSquare( self.current_focus[0], self.current_focus[1] )
            rec.border_color = self.highlightColor       

    def deHighlightFocus( self ):
        if( self.current_focus[0] != -1 and self.current_focus[1] != -1 ):
            self.getSquare( self.current_focus[0], self.current_focus[1] ).border_color = self.baseBorderColor

    @staticmethod
    def getSquareCenter( square ):
        return { square.x+square.width//2, square.y+square.height//2 }

    @staticmethod
    def delimitSquares( width, height, n, m ):
        boxes = list()

        boxes_height = height // m
        boxes_width = width // n

        for i in range( 0, n ):
            for j in range( 0, m ):
                curr = [ i*boxes_width, j*boxes_height, boxes_width, boxes_height ]
                boxes.append( curr )
        
        return boxes

    def pieceOnSquare( self, i, j ):
        for ind in range( 0, len( self.Pieces ) ):
            pc = self.Pieces[ ind ]
            if( pc[2] == i and pc[3] == j ):
                return ind

        return -1


vb = VisualBoard( 8, 8, 64, 64 )

vb.addPiece( VisualBoard.ChessPiece.whitePawn, 0, 1 )
vb.addPiece( VisualBoard.ChessPiece.blackPawn, 0, 6 )
vb.addPiece( VisualBoard.ChessPiece.whitePawn, 1, 1 )

@vb.window.event
def on_draw():
    glEnable(GL_BLEND)
    
    vb.window.clear()
    # label.draw()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    vb.batch.draw()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for i in range( 0, len(vb.Pieces) ):
        piece_info = vb.Pieces[ i ]
        cx, cy = vb.getSquareCenter( vb.getSquare( piece_info[2], piece_info[3] ) )
        piece_info[4].blit( cx, cy, 0 )

@vb.window.event
def on_mouse_press( x, y, button, modifiers):
    if( button == pyglet.window.mouse.LEFT ):
        try:
            i, j = vb.getCoordinateSquare( x, y )
            vb.deHighlightFocus()
            vb.setFocus( i, j )
            vb.highlightFocus()

            # check if a piece is on that square
            if( vb.piece_selected < 0 ):
                vb.piece_selected =  vb.pieceOnSquare( i, j )
            else:
                vb.Pieces[ vb.piece_selected ][2] = i
                vb.Pieces[ vb.piece_selected ][3] = j
                vb.piece_selected = -1
        except:
            pass
    elif( button == pyglet.window.mouse.RIGHT ):
        vb.piece_selected = -1

@vb.window.event
def on_resize(width, height):
    vb.resizeSquares( width, height )


pyglet.app.run()