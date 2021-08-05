import json
import cityflow
import gym
import numpy as np
from gym import error, spaces, utils
from gym.utils import seeding

class Cityflow(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, configPath, episodeSteps):
        #steps per episode
        self.steps_per_episode = episodeSteps
        self.is_done = False
        self.current_step = 0

        #open cityflow config file into dict
        self.configDict = json.load(open(configPath))
        #open cityflow roadnet file into dict
        self.roadnetDict = json.load(open(self.configDict['dir'] + self.configDict['roadnetFile']))
        self.flowDict = json.load(open(self.configDict['dir'] + self.configDict['flowFile']))

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

        #define action space MultiDiscrete()
        actionSpaceArray = []
        for key in self.intersections:
            actionSpaceArray.append(self.intersections[key][0][0])
        self.action_space = spaces.MultiDiscrete(actionSpaceArray)

        # define observation space
        observationSpaceDict = {}
        for key in self.intersections:
            totalCount = 0
            for i in range(len(self.intersections[key][1])):
                totalCount += len(self.intersections[key][1][i])

            intersectionObservation = []
            maxVehicles = len(self.flowDict)
            for i in range(totalCount):
                intersectionObservation.append([maxVehicles, maxVehicles])

            observationSpaceDict[key] = spaces.MultiDiscrete(intersectionObservation)
        self.observation_space = spaces.Dict(observationSpaceDict)

        # create cityflow engine
        self.eng = cityflow.Engine(configPath, thread_num=1)  

        #Waiting dict for reward function
        self.waiting_vehicles_reward = {}

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
        self.observation = self._get_observation()

        #reward
        self.reward = self.getReward()
        #Detect if Simulation is finshed for done variable
        self.current_step += 1

        if self.current_step + 1 == self.steps_per_episode:
            self.is_done = True

        #return observation, reward, done, info
        return self.observation, self.reward, self.is_done, {}

    def reset(self):
        self.eng.reset()
        return self._get_observation()

    def render(self, mode='human'):
        print("Current time: " + self.cityflow.get_current_time())

    def _get_observation(self):
        #observation
        #get arrays of waiting cars on input lane vs waiting cars on output lane for each intersection
        self.lane_waiting_vehicles_dict = self.eng.get_lane_waiting_vehicle_count()
        self.observation = {}
        for key in self.intersections:
            waitingIntersection=[]
            for i in range(len(self.intersections[key][1])):
                for j in range(len(self.intersections[key][1][i])):
                    waitingIntersection.append([self.lane_waiting_vehicles_dict[self.intersections[key][1][i][j]], 
                           self.lane_waiting_vehicles_dict[self.intersections[key][2][i][j]]])
            self.observation[key] = waitingIntersection

        return self.observation

    def getReward(self):
        reward = []
        self.vehicle_speeds = self.eng.get_vehicle_speed()
        self.lane_vehicles = self.eng.get_lane_vehicles()

        #list of waiting vehicles
        waitingVehicles = []
        reward = []

        #for intersection in dict retrieve names of waiting vehicles
        for key in self.intersections:
            for i in range(len(self.intersections[key][1])):
                #reward val
                intersectionReward = 0
                for j in range(len(self.intersections[key][1][i])):
                    vehicle = self.lane_vehicles[self.intersections[key][1][i][j]]
                    #if lane is empty continue
                    if len(vehicle) == 0:
                            continue
                    for k in range(len(vehicle)):
                        #If vehicle is waiting check for it in dict
                        if self.vehicle_speeds[vehicle[k]] < 0.1:
                            waitingVehicles.append(vehicle[k])
                            if vehicle[k] not in self.waiting_vehicles_reward:
                                self.waiting_vehicles_reward[vehicle[k]] = 1
                            else:
                                self.waiting_vehicles_reward[vehicle[k]] += 1
                            #calculate reward for intersection, cap value to -2e+200
                            if intersectionReward < -1e+200:
                                intersectionReward += -np.exp(self.waiting_vehicles_reward[vehicle[k]])
                            else:
                                intersectionReward = -1e+200
            reward.append([key, intersectionReward])

        waitingVehiclesRemove = []
        for key in self.waiting_vehicles_reward:
            if key in waitingVehicles:
                continue
            else:
                waitingVehiclesRemove.append(key)

        for item in waitingVehiclesRemove:
            self.waiting_vehicles_reward.pop(item)
        
        return reward