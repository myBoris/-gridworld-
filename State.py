import random

class State:
    def __init__(self, x, y, probabilities):
        self.x = x
        self.y = y
        self.probabilities = probabilities  # [up, down, left, right, stay]

    def choose_transition(self):
        max_prob = max(self.probabilities)
        max_indices = [i for i, prob in enumerate(self.probabilities) if prob == max_prob]
        return random.choice(max_indices), True