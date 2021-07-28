import gym_cityflow
import gym

env = gym.make('gym_cityflow:cityflow-v0', 
               configPath = 'sample_data/sample_config.json')

observation = env.step(action=1)
print(observation)