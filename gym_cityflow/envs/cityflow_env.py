import json
import cityflow
import gym
from gym import error, spaces, utils
from gym.utils import seeding

class Cityflow(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, configPath):
        #open cityflow config file into dict
        self.configDict = json.load(open(configPath))
        #open cityflow roadnet file into dict
        self.roadnetDict = json.load(open(self.configDict['dir'] + self.configDict['roadnetFile']))

        # create dict of controllable intersections and number of light phases
        self.intersections = {}
        for i in range(len(self.roadnetDict['intersections'])):
            # check if intersection is controllable
            if self.roadnetDict['intersections'][i]['virtual'] == False:
                # add intersection to dict where key = intersection_id and value = num of lightphases
                self.intersections[self.roadnetDict['intersections'][i]['id']] = len(self.roadnetDict['intersections'][i]['trafficLight']['lightphases'])

        print(self.intersections)

        eng = cityflow.Engine(configPath, thread_num=1)

        raise NotImplementedError

    def step(self, action):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError