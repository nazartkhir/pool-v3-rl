import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import pymunk
import pymunk.pygame_util
import table


class PoolEnv(gym.Env):
    def __init__(self):
        super(PoolEnv, self).__init__()
        
        # Define Action and Observation Spaces
        self.action_space = spaces.Box(
            low=np.array([-1]), 
            high=np.array([1]), 
            dtype=np.float32
        )
        self.table = table.Table()
        
        num_balls = 2 
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(2 * num_balls,), 
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        if seed is not None:
            self.np_random, seed = gym.utils.seeding.np_random(seed)
        self.table.reset()
        observation = self.table.get_observation()
        return observation, {}

    def step(self, action):
        angle = action[0]
        self.table.make_shot(angle)
        observation = self.table.get_observation()
        reward = self.table.get_reward()
        done = self.table.is_done()
        truncated = False
        info = {}
        
        return observation, reward, done, truncated, info
    
    def close(self):
        self.table.close()

# Register the environment
gym.envs.registration.register(
    id='Pool-v0',
    entry_point=PoolEnv,
)

if __name__ == "__main__":
    env = PoolEnv()
    observation, _ = env.reset()
    done = False
    i = 0
    while not done:
        action = env.action_space.sample()  # Random action
        observation, reward, done, _ = env.step(action)
        i += 1
    print(i)
    print(observation)
    