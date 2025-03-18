import gymnasium as gym
import numpy as np
import time
from stable_baselines3 import SAC
from stable_baselines3 import TD3
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.env_checker import check_env
from pool_env import PoolEnv


model = PPO.load("test1")

env  = PoolEnv(4)
#env = Monitor(env)

obs, _ = env.reset()
done = False
i = 0
while not done:
    action, _ = model.predict(np.array(obs))
    obs, reward, done, info, truncated = env.step(action)
    i += 1
    print(i)

print("Steps:", i)
env.close()