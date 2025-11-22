class Agent:
    def __init__(self, id_, x, y):
        self.id = id_
        self.x = x
        self.y = y

    @property
    def pos(self):
        return self.x, self.y

    def step(self, env):
        raise NotImplementedError
