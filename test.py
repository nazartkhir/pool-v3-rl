import gymnasium as gym
import numpy as np
from stable_baselines3 import SAC
from stable_baselines3 import TD3
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.env_checker import check_env
from pool_env import PoolEnv


env = PoolEnv(4)
env = Monitor(env)
log_dir = "./tensorboard_logs/"
model = PPO("MlpPolicy", env, verbose=1,clip_range=0.3, learning_rate=0.0003, tensorboard_log=log_dir)
model.learn(total_timesteps=10000)
model.save("test1")
env.close()




