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


model = PPO.load("pool_models/ppo_pool_n2_final")

env  = PoolEnv(2)
#env = Monitor(env)
res = []
for _ in range(5000):
    obs, _ = env.reset()
    done = False
    i = 0
    while not done:
        action, _ = model.predict(np.array(obs))
        obs, reward, done, info, truncated = env.step(action)
        i += 1

    res.append(i)
print("Steps:", np.mean(res))