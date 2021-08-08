# gym-cityflow

`gym_cityflow` is a custom OpenAI gym environment designed to handle any cityflow config file.

## Installation

`gym_cityflow` can be installed by running the following at the root directory of the repository:

`pip install -e .`

`gym_cityflow` can then be used as a python library as follows:
NOTE: configPath must be a valid cityflow `config.json` file, episodeSteps is how many steps the environment will take before it is done

```python
import gym
import gym_cityflow

env = gym.make('gym_cityflow:cityflow-v0', 
               configPath = 'sample_path/sample_config.json',
               episodeSteps = 3600)
```