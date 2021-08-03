import gym_cityflow
import gym
import sys
import os

env = gym.make('gym_cityflow:cityflow-v0', 
               configPath = 'sample_data/sample_config.json')

testAction = [0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8, 8, 8]

#disable print temporarily
#iterate environment a lttle bit to test env
for i in range(1000):
    observation, reward = env.step(action=testAction)

observation, reward = env.step(action=testAction)
print(observation)
print(reward)