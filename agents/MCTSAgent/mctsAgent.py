import socket
from random import choice
from time import sleep


class mctsAgent():
    
    HOST = "127.0.0.1"
    PORT = 1234

    _ERROR = -1
    _CONNECT = 0
    _WAIT_START = 1
    _MAKE_MOVE = 2
    _WAIT_MESSAGE = 3
    _CLOSE = 4

    def run(self):
        # A finite-state machine that cycles through waiting for input and sending moves.

        self._board_size = 0
        self._board = []
        self._colour = ""
        self._turn_count = 1
        self._choices = []

        states = {
            0: mctsAgent._connect,
            1: mctsAgent._wait_start,
            2: mctsAgent._make_move,
            3: mctsAgent._wait_message,
            4: mctsAgent._close
        }

        state = states[0](self)
        while (state != self._ERROR):
            print("Executing state:", state)
            next_state = states[state](self)
            state = next_state

    def _connect(self):
        # Connects to the socket and jumps to waiting for the start message.

        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((mctsAgent.HOST, mctsAgent.PORT))
        print("connected!")

        return self._WAIT_START

    def _wait_start(self):
        # Initialises itself when receiving the start message, then answers if it is Red or waits if it is Blue.

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            for i in range(self._board_size):
                self._board.append([])
                for j in range(self._board_size):
                    self._board[i].append(0)
                    self._choices.append((i, j))
            self._colour = data[2]

            if (self._colour == "R"):
                return self._MAKE_MOVE
            else:
                return self._WAIT_MESSAGE

        else:
            print("ERROR: No START message received.")
            return self._ERROR

    def _make_move(self):
        # Makes a random valid move. 
        
        if (self._turn_count == 2 and choice([0, 1]) == 1):
            msg = bytes("SWAP\n", "utf-8")
        else:
            move = choice(self._choices)
            msg = bytes("{},{}\n".format(move[0], move[1]).encode("utf-8"))

        self._s.sendall(msg)

        return self._WAIT_MESSAGE

    def _wait_message(self):
        # Waits for a new change message when it is not its turn.

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "END" or data[-1] == "END"):
            return self._CLOSE
        else:

            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                self._choices.remove((int(x), int(y)))

            if (data[-1] == self._colour):
                return self._MAKE_MOVE

        return self._WAIT_MESSAGE

    def _close(self):
        # Closes the socket.

        self._s.close()
        return self._ERROR

    def opp_colour(self):
        # Returns the char representation of the colour opposite to the current one.
        
        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = mctsAgent()
    agent.run()
