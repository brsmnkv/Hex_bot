# SAME AS NORMAL TIMELIMITED BUT CHECKING IF FULL EXPANDING HELPS OUT

from mctsNode import mctsNode
import random
from copy import deepcopy
import time



# Increase this a bit in any case
# fixedBranchFactor = 3

# timing


def mctsSearch(root, allowance, playouts, _c):
    c = _c
    playoutReps = playouts
    allowedtime = allowance
    start = time.monotonic()
    maxdepth = 0

    rootNode = root
    

    # print("enter mctsSearch")   #pprriinntt

    while (time.monotonic() < start + allowedtime):

        # print("iteration: " + str(i))   #pprriinntt
        # print("enter loop with iteration = " + str(i))   #pprriinntt
        
        # Selection
        selectedNode, depth = _treePolicy(rootNode, c, 1)


        # maxdepth = max(maxdepth, depth)
        # print("done selection, selected node's board: " + str(selectedNode.getBoard()))   #pprriinntt

        # Expansion

        expanded = []

        options = selectedNode.getOptions()

        for i in range(len(options)):
            child, choice = _expandPolicy(selectedNode, options)
            options.remove(choice)
            selectedNode.addChild(child)
            expanded.append(child)

        # print("Done Expansion - expanded: " + str(expanded))    #pprriinntt

        # Playout & Backpropagate for each new child
        
        for child in expanded:
            for reps in range(playoutReps):
                win = _playout(child)  
                # win is 0 or 1
                _backPropagate(child, win)

    return _best(rootNode)



def _treePolicy(root, c, i):
    currentNode = root
    while(not currentNode.isLeaf()):
        currentChildren = currentNode.getChildren()

        # HERE WE DECIDE WHICH CHILD TO PICK ON EACH ITERATION
        # IN THIS CASE WE DO THE GENERALLY AGREED UPON UCT
        # AND THERE ISN'T MUCH TO WONDER ABOUT HERE
        currentNode = max(currentChildren, key=lambda x: x.UCT(c))
        i += 1
    return currentNode, i

def _expandPolicy(selectedNode, options):

    # HERE WE PICK THE NODE(S) TO EXPAND TO FROM THE SELECTED ONE
    # FIRST WILL DO A RANDOMLY PICKED 3-5 RESULTING STATES

    # IDEALLY HERE IS WHERE WE WANT A HEURISTIC FUNCTION / NN
    # SO WE CAN BRANCH OUT TO THE IMPORTANT MOVES TO CONSIDER WITHOUT
    # BRANCHING TO UNNECESSARY ONES

    board = selectedNode.getBoard()

    choice = random.choice(options)


    # board[choice[0]][choice[1]] = 1
    
    nextNode = mctsNode(selectedNode, deepcopy(board), choice)
    nextNode.applyMove()

    return (nextNode,choice)

def _playout(child):

    board = deepcopy(child.getBoard())
    options = child.getOptions()
    colour = -1

    # WE DO A RANDOM PLAYOUT POLICY
    # THIS IS ANOTHER PLACE WHERE WE COULD IMPROVE STUFF
    # BY DOING SOMETHING BETTER THAN RANDOM
    # NOTE IM PLAYING OUT TILL FULL BOARD, BECAUSE IT MAY BE QUICKER TO DO SO,
    # THAN CHECK FOR A WINNER AFTER EVERY MOVE (ROOM FOR ANALYSIS AND IMPROVEMENT)
    while (options):
        choice = random.choice(options)
        options.remove(choice)
        board[choice[0]][choice[1]] = colour
        colour *= -1

    return _winner(board)

def _backPropagate(node, win):
    node.N += 1
    node.Q += win
    if node.parent:
        _backPropagate(node.parent, win)



def _winner(board):
    # CHECK STARTING WITH THE TOP LINE IF THERE IS A CONNECTION TO BOTTOM
    visited = set()
    left = set()

    for j in range(len(board)):
        if(board[0][j] == 1):
            left.add((0,j))

    while left:
        some = left.pop()
        visited.add(some)

        neighbours = _getNeighbours(board,some)
            
        for each in neighbours:
            if(board[each[0]][each[1]] == 1):
                if (each[0] == len(board)-1):
                    return 1
                if each not in visited:
                    left.add(each)
    return 0

def _getNeighbours(board, ij):
    x = ij[1]
    y = ij[0]
    #clockwise neighbours of a x,y
    available = [True,True,True,True,True,True]
    I_DISPLACEMENTS = [-1, -1, 0, 1,  1, 0]
    J_DISPLACEMENTS = [0,  1,  1, 0, -1, -1]
    if(y == 0): 
        available[0] = False
        available[1] = False
    elif(y == len(board)-1):
        available[3] = False
        available[4] = False
    if(x == 0):
        available[4] = False
        available[5] = False
    elif(x == len(board)-1):
        available[1] = False
        available[2] = False
    result = []
    for i in range(6):
        if available[i]:
            result.append((y+I_DISPLACEMENTS[i], x+J_DISPLACEMENTS[i]))
    return result

def _best(root):
    if root.isLeaf():
        return root
    children = root.getChildren()
    # Ill be returning the robust child for now (child with most visits)
    # thats usually a good idea
    return max(children, key=lambda x: x.Robust())

def _values(root):
    children = root.getChildren()
    outputboard = deepcopy(root.getBoard())
    for child in children:
        move = child.getMove()
        outputboard[move[0]][move[1]] = child.BestRobust()
    return outputboard
