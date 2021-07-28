import json
import cityflow
import gym
import numpy as np
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
                # for each roadLink in intersection store incoming lanes, outgoing lanes and direction in lists
                incomingLanes = []
                outgoingLanes = []
                directions = []
                for j in range(len(self.roadnetDict['intersections'][i]['roadLinks'])):
                    incomingRoads = []
                    outgoingRoads = []
                    directions.append(self.roadnetDict['intersections'][i]['roadLinks'][j]['direction'])
                    for k in range(len(self.roadnetDict['intersections'][i]['roadLinks'][j]['laneLinks'])):
                        incomingRoads.append(self.roadnetDict['intersections'][i]['roadLinks'][j]['startRoad'] + 
                                            '_' + 
                                            str(self.roadnetDict['intersections'][i]['roadLinks'][j]['laneLinks'][k]['startLaneIndex']))
                        outgoingRoads.append(self.roadnetDict['intersections'][i]['roadLinks'][j]['endRoad'] + 
                                            '_' + 
                                            str(self.roadnetDict['intersections'][i]['roadLinks'][j]['laneLinks'][k]['endLaneIndex']))
                    incomingLanes.append(incomingRoads)
                    outgoingLanes.append(outgoingRoads)

                # add intersection to dict where key = intersection_id
                # value = no of lightPhases, incoming lane names, outgoing lane names, directions for each lane group
                self.intersections[self.roadnetDict['intersections'][i]['id']] = [
                                                                                  [len(self.roadnetDict['intersections'][i]['trafficLight']['lightphases'])],
                                                                                  incomingLanes,
                                                                                  outgoingLanes,
                                                                                  directions
                                                                                 ]

        #setup intersectionNames list for agent actions
        self.intersectionNames = []
        for key in self.intersections:
            self.intersectionNames.append(key)

        # create cityflow engine
        self.eng = cityflow.Engine(configPath, thread_num=1)  

    def step(self, action):
        #Check that input action size is equal to number of intersections
        if len(action) != len(self.intersectionNames):
            raise Warning('Action length not equal to number of intersections')

        #Set each trafficlight phase to specified action
        for i in range(len(self.intersectionNames)):
            self.eng.set_tl_phase(self.intersectionNames[i], action[i])

        #env step
        self.eng.next_step()
        #observation
        #get arrays of waiting cars on input lane vs waiting cars on output lane for each intersection
        self.lane_waiting_vehicles_dict = self.eng.get_lane_waiting_vehicle_count()
        self.observation = []
        for key in self.intersections:
            waitingIntersection=[]
            waitingIntersection.append(key)
            for i in range(len(self.intersections[key][1])):
                for j in range(len(self.intersections[key][1][i])):
                    waitingIntersection.append([self.lane_waiting_vehicles_dict[self.intersections[key][1][i][j]], 
                           self.lane_waiting_vehicles_dict[self.intersections[key][2][i][j]]])
            self.observation.append(waitingIntersection)

        #TODO: create reward function

        #TODO: Detect if Simulation is finshed for done variable

        #return observation, reward, done, info
        return self.observation

    def reset(self):
        raise NotImplementedError

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError