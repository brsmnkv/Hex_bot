"""
A MonteCarloTreeSearch Node class:
- Q and N are total reward and visits to node, from basic algorithm
- children are the existing / already created children nodes of that node
- options are all the possible children nodes (MAYBE)
- parent is the parent node - for backpropagation (none for root)
- board - the state the node represents
"""

class mctsNode:

    def __init__(self, _parent, _board):
        self.Q = 0
        self.N = 0
        self.children = []
        self.parent = _parent

        self.options = []
        #generate options (MAYBE)

        self.board = _board


    def addChild(self, _child):
        self.children.append(somechild)

    def playout(self):
        # playout from this node's board to end

    def backpropagate(self):
        # update this node's data and then backpropagate to its parent (unless root)    

