import gym_cityflow
import gym
import sys
import os
import random

env = gym.make('gym_cityflow:cityflow-v0', 
               configPath = 'sample_data/sample_config.json',
               episodeSteps = 1000)

#Check action space
print(env.action_space)

#disable print temporarily
#iterate environment a lttle bit to test env
actionInterval = 10

for i in range(10000):
    if i % actionInterval == 0:
        testAction = []
        for i in range(0,16):
            n = random.randint(0,8)
            testAction.append(n)
    observation, reward, done, debug = env.step(action=testAction)
    if done:
        break

observation, reward, done, debug = env.step(action=testAction)
print(observation)
print(reward)