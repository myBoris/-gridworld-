import time

from State import State


class StateMachine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.states = [[State(x, y, [1, 1, 1, 1, 1]) for y in range(height)] for x in range(width)]

    def set_initial_state(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.current_x = x
            self.current_y = y
        else:
            raise ValueError("Initial state is out of bounds")

    def transition(self, x, y):
        state = self.states[x][y]
        direction, isLoop = state.choose_transition()

        # action = ['','↑','↓', '←', '→', '●']

        #           '↑'      '↓'     '←'      '→'     '●'
        dx, dy = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)][direction]

        new_x, new_y = x + dx, y + dy

        if 0 <= new_x < self.width and 0 <= new_y < self.height:
            return x, y, new_x, new_y, direction, isLoop
        return x, y, x, y, direction, isLoop

    def iterate(self, start_x, start_y, callback=None):
        path = [(start_x, start_y)]
        current_x, current_y = start_x, start_y
        self.set_initial_state(start_x,start_y)

        isLoop = True
        while(isLoop):
            pre_x, pre_y, current_x, current_y, direction, isLoop = self.transition(current_x, current_y)
            path.append((current_x, current_y))
            if callback is not None:
                callback(pre_x, pre_y, current_x, current_y, direction + 1)

            time.sleep(3)

        return path