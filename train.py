import gymnasium as gym
import numpy as np
import torch # PyTorch is usually the default backend for SB3
import os

# Import the custom environment
try:
    # Assumes pool_env.py is in the same directory or accessible via PYTHONPATH
    from pool_env import PoolEnv
except ImportError:
    print("Error: Could not import PoolEnv.")
    print("Make sure pool_env.py is in the same directory or your PYTHONPATH is set correctly.")
    exit()

# Import Stable Baselines3 components
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.env_util import make_vec_env
    from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
    from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
    from stable_baselines3.common.monitor import Monitor # <-- Import Monitor
except ImportError:
    print("Error: Could not import Stable Baselines3 components.")
    print("Please install stable-baselines3: pip install stable-baselines3[extra]")
    exit()


if __name__ == "__main__":
    # --- Configuration ---
    NUM_BALLS = 4 # Total balls (1 cue + 2 target balls). Adjust as needed.
    NUM_CPU = 4    # Number of parallel environments (adjust based on your CPU cores)
    TOTAL_TIMESTEPS = 200000 # Total training steps (increase for better results)
    MODEL_NAME = f"ppo_pool_n{NUM_BALLS}v2"
    LOG_DIR = "./pool_logs/"
    MODEL_SAVE_DIR = "./pool_models/"
    SAVE_FREQ = 100000 # Save a checkpoint every N steps

    # Create directories if they don't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

    print(f"Starting training for {NUM_BALLS} balls.")
    print(f"Using {NUM_CPU} parallel environments.")
    print(f"Total timesteps: {TOTAL_TIMESTEPS}")

    # --- Environment Setup ---
    # Function to create a single environment instance, now wrapped with Monitor
    def make_env(rank, seed=0):
        def _init():
            # Create the base environment
            env = PoolEnv(n=NUM_BALLS)
            # Important: Seed the environment for reproducibility
            # Note: Monitor wrapper handles seeding the underlying env if seed is passed to reset
            # env.reset(seed=seed + rank) # Seeding done by Monitor/VecEnv now

            # Wrap the environment with Monitor
            # Log files will be saved in LOG_DIR/monitor_{rank}.csv
            log_file_path = os.path.join(LOG_DIR, f"monitor_{rank}") # Use rank in filename
            env = Monitor(env, filename=log_file_path)
            return env
        return _init

    # Create the vectorized environments
    # Pass the seed to SubprocVecEnv/DummyVecEnv, which handles seeding Monitor/BaseEnv
    if NUM_CPU > 1:
        print("Using SubprocVecEnv for parallel environments.")
        # Seed is handled by the VecEnv wrapper now
        vec_env = SubprocVecEnv([make_env(i) for i in range(NUM_CPU)])
    else:
        print("Using DummyVecEnv for a single environment.")
        vec_env = DummyVecEnv([make_env(0)])


    # Optional: Normalize observations and rewards. PPO can benefit from this.
    # Note: If you use VecNormalize, you MUST save/load the normalization stats along with the model.
    # print("Applying VecNormalize.")
    # vec_env = VecNormalize(vec_env, norm_obs=True, norm_reward=True, gamma=0.99) # Adjust gamma if needed

    # --- Model Definition ---
    # PPO hyperparameters (these often require tuning)
    # See SB3 documentation for details: https://stable-baselines3.readthedocs.io/en/master/modules/ppo.html
    model = PPO(
        "MlpPolicy",            # Multi-Layer Perceptron policy network
        vec_env,
        verbose=1,              # Print training progress (0=no output, 1=info, 2=debug)
        n_steps=2048,           # Steps collected per environment before updating policy
        batch_size=64,          # Minibatch size for policy updates
        n_epochs=10,            # Number of optimization epochs per update
        gamma=0.99,             # Discount factor for future rewards
        gae_lambda=0.95,        # Factor for Generalized Advantage Estimation
        clip_range=0.2,         # Clipping parameter for PPO loss
        ent_coef=0.0,           # Entropy coefficient (encourages exploration) - start low
        learning_rate=3e-4,     # Learning rate for the optimizer (Adam)
        tensorboard_log=LOG_DIR,# Directory for TensorBoard logs
        device="auto"           # Use GPU if available ("cuda"), otherwise "cpu"
    )

    print(f"PPO Model Created. Policy architecture: {model.policy}")
    print(f"Logging to: {LOG_DIR}")
    print(f"Saving models to: {MODEL_SAVE_DIR}")

    # --- Callbacks ---
    # Save a checkpoint periodically
    checkpoint_callback = CheckpointCallback(
        save_freq=max(SAVE_FREQ // NUM_CPU, 1), # Adjust frequency based on vec envs
        save_path=MODEL_SAVE_DIR,
        name_prefix=MODEL_NAME
    )

    # Optional: Evaluate the model periodically on a separate environment
    # eval_env = PoolEnv(n=NUM_BALLS) # Create a single env for evaluation
    # eval_env = Monitor(eval_env, os.path.join(LOG_DIR, "eval_monitor")) # Wrap eval env too!
    # eval_env = DummyVecEnv([lambda: eval_env])
    # if isinstance(vec_env, VecNormalize): # Need to wrap eval env if training env is normalized
    #     eval_env = VecNormalize(eval_env, training=False, norm_obs=True, norm_reward=False, gamma=0.99)
    # eval_callback = EvalCallback(eval_env, best_model_save_path=MODEL_SAVE_DIR + 'best_model/',
    #                              log_path=LOG_DIR + 'eval/', eval_freq=max(10000 // NUM_CPU, 1),
    #                              deterministic=True, render=False)


    # --- Training ---
    print("Starting Training...")
    try:
        model.learn(
            total_timesteps=TOTAL_TIMESTEPS,
            callback=checkpoint_callback, # Add eval_callback here if using it
            log_interval=1, # Log stats every 'log_interval' updates
            tb_log_name=MODEL_NAME # Name for the TensorBoard run
        )
    except KeyboardInterrupt:
        print("Training interrupted by user.")
    finally:
        # --- Save Final Model ---
        final_model_path = os.path.join(MODEL_SAVE_DIR, f"{MODEL_NAME}_final")
        print(f"Saving final model to: {final_model_path}")
        model.save(final_model_path)

        # Important: Save VecNormalize statistics if it was used
        # if isinstance(vec_env, VecNormalize):
        #     stats_path = os.path.join(MODEL_SAVE_DIR, f"{MODEL_NAME}_final_vecnormalize.pkl")
        #     print(f"Saving VecNormalize stats to: {stats_path}")
        #     vec_env.save(stats_path)

        # Close the environment(s)
        vec_env.close()
        # if 'eval_env' in locals() and eval_env is not None:
        #     eval_env.close()

    print("Training finished.")
    print(f"To view logs, run: tensorboard --logdir {LOG_DIR}")

