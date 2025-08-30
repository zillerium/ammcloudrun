# rl_test.py
from rl_agent import GridWorld, Agent

env = GridWorld(6, 5, [(0,2),(0,3),(1,2),(2,4),(3,2),(4,2),(5,3)])
agent = Agent(env)
path = agent.act()
print("Test path:", path)

