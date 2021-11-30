"""
A MonteCarloTreeSearch Node class:
- Q and N are total reward and visits to node, from basic algorithm
- children are the existing / already created children nodes of that node
- options are all the possible children nodes (MAYBE)
- parent is the parent node - for backpropagation (none for root)
"""

class mctsNode:

    def __init__(self, mctsNode _parent):
        self.Q = 0
        self.N = 0
        self.options = []
        self.children = []
        self.parent = _parent

        #generate options (MAYBE)