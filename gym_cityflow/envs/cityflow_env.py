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
                # for each roadLink in intersection store incoming lanes and outgoing lanes in lists
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
                print(incomingLanes)
                print(outgoingLanes)
                print(directions)

                # add intersection to dict where key = intersection_id
                # value = lightPhases
                self.intersections[self.roadnetDict['intersections'][i]['id']] = len(self.roadnetDict['intersections'][i]['trafficLight']['lightphases'])
                


        
        
        print(len(self.roadnetDict['intersections'][5]['roadLinks']))
        print(self.roadnetDict['intersections'][5]['roadLinks'][1]['type'])
        print(self.roadnetDict['intersections'][5]['roadLinks'][1]['startRoad'])
        print(self.roadnetDict['intersections'][5]['roadLinks'][1]['endRoad'])
        print(len(self.roadnetDict['intersections'][5]['roadLinks'][1]['laneLinks']))
        print(self.roadnetDict['intersections'][5]['roadLinks'][1]['laneLinks'][0]['startLaneIndex'])

        testLane = self.roadnetDict['intersections'][5]['roadLinks'][1]['startRoad'] + '_' + str(self.roadnetDict['intersections'][5]['roadLinks'][1]['laneLinks'][0]['startLaneIndex'])

        eng = cityflow.Engine(configPath, thread_num=1)

        for i in range(1000):
            eng.next_step()

        self.lane_waiting_vehicles_dict = eng.get_lane_waiting_vehicle_count()
        print(self.lane_waiting_vehicles_dict[testLane])
        self.waitingDict = eng.get_lane_vehicles()
        print(eng.get_vehicle_info("flow_1_0"))


        raise NotImplementedError

    def step(self, action):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def render(self, mode='human'):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError