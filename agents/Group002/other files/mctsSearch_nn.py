# class Net(nn.Module):
#   def __init__(self,board_size=15):
#     super(Net, self).__init__()
#     self.board_size = board_size
#     self.conv = nn.Conv2d(1, 1 , 5, stride=1)
#     self.conv2 = nn.Conv2d(1, 1, 1, stride=1)
#     self.linear = nn.Linear(11**2,11**2)

#   def forward(self,input):
   
#     output = self.conv(input)
#     output = self.conv2(output)
#     output = torch.flatten(output,start_dim=2,end_dim=3)
#     output = self.linear(output.squeeze(0).squeeze(0))
  
#     return output


def mctsSearch(root, allowance, playouts, fixedbranching, _c, expand_to):
    rootNode = root
    c = _c
    # expansion_n = 121
    expansion_n = expand_to
    allowedtime = allowance
    start = time.monotonic()
    playoutReps = playouts
    fixedBranchFactor = fixedbranching
    opponent = 0
     
    #LOAD THE MODEL FOR USE
    network = Net()
    network.load_state_dict(torch.load('/content/params'), strict=False)
 
    

    
    while (time.monotonic() < start + allowedtime):


        # print("enter loop with iteration = " + str(i))
        
        # Selection
        selectedNode, depth = _treePolicy(rootNode, c, 1)

        """
                root (1) (our turn)
                / |  \ 
               1   1   1  (2) (opponent's turn)
               / \
             -1  -1    (3)   
        """
        opponent = not depth%2
        
        # Expansion

        expanded = []
        options = selectedNode.getOptions()

        # # Potentially we want to get fewer options down the line
        # expansion_n = int(len(options)/depth)
    
        if opponent:  #if opponent - we want to work with reverse board
            selectedNode.revBoard()
        network_moves = _expandPolicy(selectedNode,options,expansion_n,network)

        for pair in network_moves:
            child, choice = pair

            if opponent:    #if opponent - revert children to normal
                child.revBoard()
                choice[0], choice[1] = choice[1], choice[0]

            options.remove(choice)
            selectedNode.addChild(child)
            expanded.append(child)
        
        if opponent:  #if opponent - revert reverse board
            selectedNode.revBoard()

        # print("Done Expansion - expanded: " + str(expanded))



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

def net_board_rep(board=None):  
    player_num = 1
    opp_player_num = -1

    board_rep = board.print_board().split(',')
    int_rep =[]
    for i in range(board._board_size):
      str_row = board_rep[i]
      row = []
      for j in range(board._board_size):
        row.append(board[i,j])

      row.insert(0,-1.0)
      row.insert(0,-1.0)
      row.append(-1.0)
      row.append(-1.0)
      int_rep.append(row)
 
    # pad_top_bottom
    vert_border = [1.0 for i in range(board._board_size)]
    vert_border.insert(0,0.0)
    vert_border.insert(0,0.0)
    vert_border.append(0.0)
    vert_border.append(0.0)

    int_rep.insert(0,vert_border)
    int_rep.insert(0,vert_border)
    int_rep.append(vert_border)
    int_rep.append(vert_border)

    board_array = np.array(int_rep)
    return board_array

def _expandPolicy(selectedNode,options,number=None,network=None):

    # HERE WE PICK THE NODE(S) TO EXPAND TO FROM THE SELECTED ONE
    # FIRST WILL DO A RANDOMLY PICKED 3-5 RESULTING STATES

    # IDEALLY HERE IS WHERE WE WANT A HEURISTIC FUNCTION / NN
    # SO WE CAN BRANCH OUT TO THE IMPORTANT MOVES TO CONSIDER WITHOUT
    # BRANCHING TO UNNECESSARY ONES

    board = selectedNode.getBoard()

    #return 121 options
    board_rep = net_board_rep(board)
    network = model(board_rep)
    #Epsillon Greedy
    #RANDOM ACTION
    expand_list = []
    expand = 0
    exhausted = False
    while(exhausted != True and len(expand_list) < number):
      # if (random.random() > 0.80):
      #   #ONLY TRY 40 TIMES TO PREVENT INFINITE LOOP
      #   tried = 0
      #   action = int(np.random.randint(0,121))
      #   move_to_make = (int(action/11),action%11)
      #   while(state1[move_to_make[0]+2,move_to_make[1]+2] != 0 and tried < 40):
      #     action = int(np.random.randint(0,121))
      #     move_to_make = (int(action/11),action%11)
      #     tried += 1
      
      #ELSE TAKE NEXT AVAILABLE BEST 
      #IF NONE AVAILABLE STOP
      moves = network(board_rep.unsqueeze(0).unsqueeze(0).float())
      # else:
      actions = torch.topk(moves, 121).indices
      action = int(actions[0])
      i = 0
      #MOVE IN BOARD TERMS
      move_to_make = (int(action/11),action%11)
      while((i < 121) and (state1[move_to_make[0]+2,move_to_make[1]+2] != 0)):
        action = int(actions[i])
        #MOVE IN BOARD TERMS
        move_to_make = (int(action/11),action%11)
        i+=1
      #IF NO AVAILABLE BEST 
      if i == 121:
        exhausted = True
      nextNode = mctsNode(selectedNode, deepcopy(board))
      nextNode.board[move_to_make[0]][move_to_make[1]] = 1
      expand_list.append((nextNode,move_to_make))

    return expand_list

    # else:
    #   choice = random.choice(options)
    #   # board[choice[0]][choice[1]] = 1
    
    #   nextNode = mctsNode(selectedNode, deepcopy(board))
    #   nextNode.board[choice[0]][choice[1]] = 1

    #   return (nextNode,choice)

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



def _best(root):
    if root.isLeaf():
        return root
    children = root.getChildren()
    # Ill be returning the robust child for now (child with most visits)
    # thats usually a good idea
    return max(children, key=lambda x: x.Robust())



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