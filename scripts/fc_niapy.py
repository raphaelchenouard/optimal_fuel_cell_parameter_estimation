from pemfc import PEMFC

from niapy.problems import Problem
from niapy import Runner
from niapy.algorithms.basic import (
    GreyWolfOptimizer,
    ParticleSwarmAlgorithm
)

class NiapyPEMFC(Problem):
    def __init__(self, fc: PEMFC):
        super().__init__(7,
            np.array([-1.1997, 1, 3.6, -26, 0.1, 13, 0.0136]),
            np.array([-0.8532, 5, 9.8, -9.54, 0.8, 23, 0.5]))
        self.fc = fc
        self.name = fc.name

    def _evaluate(self, x):
        self.fc.parameters = np.array(x)
        return self.fc.sum_squared_error()
    def name(self):
            """Get class name."""
            return self.__class__.__name__+self.name

import time
import json
import sys
import numpy as np


if __name__=='__main__':
    fc_datafiles = {'H-12': 'h-12.json', 'ps6': 'ps6.json', '250W': '250W.json'}

    fc_name='250W'
    if len(sys.argv)==2:
        fc_name = sys.argv[1]

    print('Fuel cell selected:', fc_name)

    data_path='../data/'

    with open(data_path+fc_datafiles[fc_name],'r') as f:
        json_string = f.read()
    fc_data = json.loads(json_string)
    fc = PEMFC(fc_data['name'],N_s=fc_data['N_s'],A=fc_data['A'],l=fc_data['l'],J_max=fc_data['J_max'])
    fc.set_experimental_conditions(T=fc_data['T'],P_O_2=fc_data['P_O_2'],P_H_2=fc_data['P_H_2'])
    fc.V_exp = np.array(fc_data['V_exp'])
    fc.I_exp = np.array(fc_data['I_exp'])

    fc_pb = NiapyPEMFC(fc)

    runner = Runner(
        dimension=7,
        max_evals=10000,
        runs=20,
        algorithms=[
            GreyWolfOptimizer(),
            "FlowerPollinationAlgorithm",
            ParticleSwarmAlgorithm(),
            "MothFlameOptimizer",
            "BacterialForagingOptimization"],
        problems=[
            fc_pb
        ]
    )

    runner.run(export='json', verbose=True)
