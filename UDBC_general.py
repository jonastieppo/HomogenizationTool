# %%
from dataTypes import NodeList, Node
import pandas as pd
import numpy as np

class  UDBC_general():
    '''

    '''
    def __init__(self, nodes : NodeList) -> None:        
        self.nodeDataFrame = pd.DataFrame(data = nodes)
        pass

    def __defineNodeDisplacements(self, nodeInfo : Node, strainTensor: np.array):
        node_coordinates = np.array([nodeInfo['x'], nodeInfo['y'], nodeInfo['z']])
        return np.matmul(strainTensor,node_coordinates)
    
    def __findBoundaryNodes(self, nodes : NodeList):
        '''
        Method to find the boundary nodes bases on node coordinates. It works, however, only for hexadrical-like
        RVE. For an general geometry, further efforts has to de done.
        '''
        x_max = nodes['x_s'].max()
        pass


# teste = UDBC_general(pd.DataFrame())

# %%

# %%
