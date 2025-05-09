import gymnasium as gym
import numpy as np
import torch
import os

try:
    from pool_env import PoolEnv
except ImportError:
    print("Error: Could not import PoolEnv.")
    print("Make sure pool_env.py is in the same directory or your PYTHONPATH is set correctly.")
    exit()
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
    from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
    from stable_baselines3.common.monitor import Monitor
except ImportError:
    print("Error: Could not import Stable Baselines3 components.")
    print("Please install stable-baselines3: pip install stable-baselines3[extra]")
    exit()


if __name__ == "__main__":
    NUM_BALLS = 4
    NUM_CPU = 4
    TOTAL_TIMESTEPS = 200000
    MODEL_NAME = f"ppo_pool_n{NUM_BALLS}v2"
    LOG_DIR = "./pool_logs/"
    MODEL_SAVE_DIR = "./pool_models/"
    SAVE_FREQ = 100000

    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    print(f"Starting training for {NUM_BALLS} balls.")
    print(f"Using {NUM_CPU} parallel environments.")
    print(f"Total timesteps: {TOTAL_TIMESTEPS}")
    def make_env(rank, seed=0):
        def _init():
            env = PoolEnv(n=NUM_BALLS)

            log_file_path = os.path.join(LOG_DIR, f"monitor_{rank}")
            env = Monitor(env, filename=log_file_path)
            return env
        return _init
    if NUM_CPU > 1:
        print("Using SubprocVecEnv for parallel environments.")
        vec_env = SubprocVecEnv([make_env(i) for i in range(NUM_CPU)])
    else:
        print("Using DummyVecEnv for a single environment.")
        vec_env = DummyVecEnv([make_env(0)])
    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        learning_rate=3e-4,
        tensorboard_log=LOG_DIR,
        device="auto"           
    )

    print(f"PPO Model Created. Policy architecture: {model.policy}")
    print(f"Logging to: {LOG_DIR}")
    print(f"Saving models to: {MODEL_SAVE_DIR}")

    checkpoint_callback = CheckpointCallback(
        save_freq=max(SAVE_FREQ // NUM_CPU, 1),
        save_path=MODEL_SAVE_DIR,
        name_prefix=MODEL_NAME
    )

    print("Starting Training...")
    try:
        model.learn(
            total_timesteps=TOTAL_TIMESTEPS,
            callback=checkpoint_callback,
            log_interval=1,
            tb_log_name=MODEL_NAME 
        )
    except KeyboardInterrupt:
        print("Training interrupted by user.")
    finally:
        final_model_path = os.path.join(MODEL_SAVE_DIR, f"{MODEL_NAME}_final")
        print(f"Saving final model to: {final_model_path}")
        model.save(final_model_path)
        vec_env.close()

    print("Training finished.")
    print(f"To view logs, run: tensorboard --logdir {LOG_DIR}")

