# %%
from dataTypes import NodeList, Node, BoundaryConditions
import pandas as pd
import numpy as np
class  UDBC_general():
    '''

    '''
    def __init__(self, nodes : NodeList) -> None:        
        self.nodeDataFrame = pd.DataFrame(data = nodes)
        self.nodeDataFrame['n'].astype(int)
        self.bcDataFrame : BoundaryConditions = {}
        self.__applyBoundaryConditions()
        pass

    def __findBodyDimensions(self):
        '''
        Method to find body lenght
        '''
        self.x_l = abs(self.nodeDataFrame['x'].max()-self.nodeDataFrame['x'].min())
        self.y_l = abs(self.nodeDataFrame['x'].max()-self.nodeDataFrame['x'].min())
        self.z_l = abs(self.nodeDataFrame['x'].max()-self.nodeDataFrame['x'].min())

    def __findCentroid(self):
        '''
        Finds the body centroids
        '''
        self.x_c = self.nodeDataFrame['x'].mean()
        self.y_c = self.nodeDataFrame['y'].mean()
        self.z_c = self.nodeDataFrame['z'].mean()

    def __nodeCoordinatesByCentroid(self, nodeInfo : Node):
        '''
        Compute the coordinates relatively to body centoids
        '''
        return np.array([nodeInfo['x']-self.x_c, nodeInfo['y']-self.y_c, nodeInfo['z']-self.z_c])

    def __defineNodeDisplacements(self, nodeInfo : Node):
        node_coordinates = self.__nodeCoordinatesByCentroid(nodeInfo)
        disp = np.matmul(self.strainTensor,node_coordinates)
        nodeInfo['u1'] = disp[0]/self.x_l
        nodeInfo['u2'] = disp[1]/self.y_l
        nodeInfo['u3'] = disp[2]//self.z_l
        return nodeInfo
    
    def __findBoundaryNodes(self)->pd.DataFrame:
        '''
        Method to find the boundary nodes bases on node coordinates. It works, however, only for hexadrical-like
        RVE. For an general geometry, further efforts has to de done.
        '''
        x_max = self.nodeDataFrame['x'].max()
        x_min = self.nodeDataFrame['x'].min()
        y_max = self.nodeDataFrame['y'].max()
        y_min = self.nodeDataFrame['y'].min()
        z_max = self.nodeDataFrame['z'].max()
        z_min = self.nodeDataFrame['z'].min()
        
        boolCondition_x  = np.add(self.nodeDataFrame['x']==x_max,self.nodeDataFrame['x']==x_min)
        boolCondition_y  = np.add(self.nodeDataFrame['y']==y_max,self.nodeDataFrame['y']==y_min)
        boolCondition_z  = np.add(self.nodeDataFrame['z']==z_max,self.nodeDataFrame['z']==z_min)
        boolCondition = np.add(np.add(boolCondition_x,boolCondition_y),boolCondition_z)

        return self.nodeDataFrame[boolCondition]

    def __applyBoundaryConditions(self):
        '''
        Method to apply the boundary conditions over a body
        '''
        boundaryNodes = self.__findBoundaryNodes()
        self.__findCentroid()
        self.__findBodyDimensions()

        strain_cases,strain_names = self.__defineStrainTensors()

        for each_strain_case, strain_case_name in zip(strain_cases,strain_names):
            self.strainTensor = each_strain_case
            self.bcDataFrame[strain_case_name]=(boundaryNodes.apply(self.__defineNodeDisplacements, axis=1))

    def __defineStrainTensors(self)->list[np.array]:
        '''
        return a list of strain tensors
        '''
        Exx = np.array([[1,0,0],
                        [0,0,0],
                        [0,0,0],
                        ]) 
        return [Exx],['Exx']

def createNewMesh(nodesInAdirection = 10):
    data : NodeList = {} 
    nnodes = nodesInAdirection**3
    data['n']=np.linspace(1,nnodes,nnodes).astype('int')
    data['x']=np.zeros((nnodes))
    data['y']=np.zeros((nnodes))
    data['z']=np.zeros((nnodes))
    counter = 0
    for z in range(nodesInAdirection):
        for y in range(nodesInAdirection):
            for x in range(nodesInAdirection):
                data['x'][counter] = x
                data['y'][counter] = y
                data['z'][counter] = z
                counter+=1

    return data


if __name__=='__main__':
    mesh = pd.DataFrame(createNewMesh())
    teste = UDBC_general(mesh)

# %%

# %%
