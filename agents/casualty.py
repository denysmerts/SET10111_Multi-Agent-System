from .agent import Agent

class Casualty(Agent):
    def __init__(self, x, y):
        super().__init__(id_=0, x=x, y=y)

    def step(self, env):
        pass  
