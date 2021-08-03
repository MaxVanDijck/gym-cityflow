import gym_cityflow
import gym
import sys
import os
import random

env = gym.make('gym_cityflow:cityflow-v0', 
               configPath = 'sample_data/sample_config.json')

testAction = []
for i in range(0,16):
    n = random.randint(0,8)
    testAction.append(n)
#disable print temporarily
#iterate environment a lttle bit to test env
for i in range(1000):
    testAction = []
    for i in range(0,16):
        n = random.randint(0,8)
        testAction.append(n)
    observation, reward = env.step(action=testAction)

observation, reward = env.step(action=testAction)
print(observation)
print(reward)