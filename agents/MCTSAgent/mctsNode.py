"""
A MonteCarloTreeSearch Node class:
- Q and N are total reward and visits to node, from basic algorithm
- children are the existing / already created children nodes of that node
- options are all the possible children nodes (MAYBE)
- parent is the parent node - for backpropagation (None for root)
- board - the state the node represents
"""

from math import sqrt, log

class Board:
    def __init__(self, _board):
        self.board = []
        self.size = len(_board)
        for i in range(len(_board)):
            for j in range(len(_board)):
                self.board.append(_board[i][j])



    def getPiece(self, i,j):
        return self.board[i*self.size + j]

    def setPiece(self, piece, i,j):
        self.board[i*self.size + j] = piece

    def getBoard(self):
        return self.board

    def size(self):
        return self.size

        

class mctsNode:

    def __init__(self, _parent, _board, move):
        self.Q = 0
        self.N = 0
        self.children = []
        self.parent = _parent
        self.leaf = True
        self.size = len(_board)
        self.move = move

        self.options = []
        #generate options (MAYBE)

        # we want board to be a matrix of -1,0,1s
        self.board = _board

    def applyMove(self):
        self.board[self.move[0]][self.move[1]] = 1

    def getMove(self):
        return self.move


    def addChild(self, _child):
        self.children.append(_child)
        self.leaf = False

    def getChildren(self):
        return self.children

    def isLeaf(self):
        return self.leaf
    
    def isRoot(self):
        return self.parent is None

    def UCT(self, c):
        return (self.Q / self.N) + c*sqrt(2*log(self.parent.N)/self.N)

    def Robust(self):
        return self.N

    def BestRobust(self):
        return (self.Q,self.N)

    def getBoard(self):
        return self.board

    def getOptions(self):
        options = []
        for i in range(self.size):
            for j in range(self.size):
                if(self.board[i][j] == 0):
                    options.append((i,j))
        return options

    # def playout(self):
    #     # playout from this node's board to end

    # def backpropagate(self):
    #     # update this node's data and then backpropagate to its parent (unless root)    
