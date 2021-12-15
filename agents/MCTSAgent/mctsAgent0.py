import socket
from random import choice
from time import sleep
from mctsNode import mctsNode
import mctsSearch_Basic_timelimited as mcts_t
# from mctsSearch_Basic_timelimited import mctsSearch


class mctsAgent0():
    
    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        # A finite-state machine that cycles through waiting for input and sending moves.
        
        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []
        self._swapped = 0
        
        states = {
            1: mctsAgent0._connect,
            2: mctsAgent0._wait_start,
            3: mctsAgent0._make_move,
            4: mctsAgent0._wait_message,
            5: mctsAgent0._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        # Connects to the socket and jumps to waiting for the start message.
        
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((mctsAgent0.HOST, mctsAgent0.PORT))

        return 2

    def _wait_start(self):
        # Initialises itself when receiving the start message, then answers if it is Red or waits if it is Blue.
        
        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            for i in range(self._board_size):
                self._board.append([])
                for j in range(self._board_size):
                    # create a board [][] filled with zeros, and add the i,j to choices
                    self._board[i].append(0)
                    self._choices.append((i, j))
            self._colour = data[2]

            # If "R" (first) or "B" - (second)
            # TODO first asignment of colours
            if (self._colour == "R"):
                return 3
            else:

                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        # Makes a random valid move. 
        
        # 50% chance to change if move == 2
        if (self._turn_count == 2 and choice([0, 1]) == 1):
            msg = "SWAP\n"

        # Any other move:
        else:
            # move = choice(self._choices)
            root = mctsNode(None, self._board, None)
            child = mcts_t.mctsSearch(root,1,1,0.1)
            move = self._ij(child.getMove())
            msg = f"{move[0]},{move[1]}\n"
        
        self._s.sendall(bytes(msg, "utf-8"))

        return 4
        

    def _wait_message(self):
        # Waits for a new change message when it is not its turn.

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:

            if (data[1] == "SWAP"):
                # swap sides/ board rep
                self._colour = self.opp_colour()
                self._swap_board()
                self._swapped = 1

            else:

                # TODO a normal x,y move has been accepted - update board
                i, j = data[1].split(",")
                self._choices.remove((int(i), int(j)))
                ni,nj = self._ij((int(i),int(j)))
                currentp = self._other_player(data[3])
                self._board[ni][nj] = self._01(currentp)


            if (data[-1] == self._colour):
                return 3

        return 4

    def _close(self):
        # Closes the socket.

        self._s.close()
        return 0

    def opp_colour(self):
        # Returns the char representation of the colour opposite to the current one.
        
        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"

    def _other_player(self, colour):
        if colour == "R":
            return "B"
        elif colour == "B":
            return "R"
        else:
            return "None"

    def _ij(self, pair):
        # returns i,j or j,i depending on R or B for internal board rep access
        # normal => return pair
        if self._colour == "R":
            return pair
        # reversed => return (pair[1],pair[0])
        elif self._colour == "B":
            return (pair[1],pair[0])
        else:
            return "None"
    
    def _01(self, turn):
        if turn == self._colour:
            return 1
        else:
            return -1

    def _swap_board(self):
        # swap board diagonally and change 1s and -1s (for colour change)
        for i in range(self._board_size):
            for j in range(i+1, self._board_size):
                self._board[i][j],self._board[j][i] = self._board[j][i],self._board[i][j]
        for i in range(self._board_size):  
            for j in range(self._board_size):
                self._board[i][j] *= -1



if (__name__ == "__main__"):
    agent = mctsAgent0()
    agent.run()
