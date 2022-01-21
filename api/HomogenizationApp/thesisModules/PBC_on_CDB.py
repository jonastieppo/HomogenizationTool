#!/usr/bin/env python
# coding: utf-8

'''
In this version, the will be to define method to all operations, mainly the first geometrical entities. After this, integrate with
the rest of the code. Further, I will store the paired entities and request when needed to write the APDL Commands. 
As a sequence, this code can be described as three steps:

1) Identify All geometric boundaries and Entities (Faces, Edges and Nodes)
2) Identify the paired nodes in domain, and store them
3) Write APDL Commands and Solve
4) Post-processing Results

'''
import pandas as pd
import numpy as np
from time import perf_counter
from tqdm import tqdm


def GetGeometryMacro(macro_name,macro_folder):
    '''
    Method to store the macroname and the folder where it is in two strings. Of course,
    it will returns two strings. 
    '''
    return macro_name,macro_folder


def SetTOL(tol):
    '''
    Method to set the model tolerance to find paired nodes
    '''
    global tol_global
    tol_global = tol

    return tol_global


def GetNodeDataFromCDB(macro_folder,cdbname):
    '''
    A method to extract the node data from a default .cdb ansys output.
    '''
    with open("{}\{}.cdb".format(macro_folder,cdbname),"r") as myfile:
        data = myfile.readlines()
        data = np.array(data)

    for row in range(0, data.shape[0]):
        if data[row] == '(3i9,6e21.13e3)\n':
            nodebegin = row
        if data[row] == '(19i9)\n':
            elementbegin = row

    nodedata = data[nodebegin+1:elementbegin-2]
    
    return nodedata


def CreatDataframeFromNodeData(nodedata):
    '''
    A method to creat a dataframe from a nodedata originated in ansys APDL
    '''
    
    f= open("nodecood.tmp","w")

    for i in range(0,nodedata.shape[0]):
        f.write("{}".format(nodedata[i]))
    f.close()

    global nodedataframe

    nodedataframe = pd.read_fwf("nodecood.tmp",widths=[9,9,9,21,21,21], header=None)

    nodedataframe = nodedataframe.fillna(0)

    nodedataframe = nodedataframe.drop(columns = [1,2])

    #Naming columns to makes things clear

    data = {"NodeNumber":nodedataframe.iloc[:,0],
           "X":nodedataframe.iloc[:,1],
           "Y":nodedataframe.iloc[:,2],
           "Z":nodedataframe.iloc[:,3]}

    nodedataframe = pd.DataFrame(data=data)

    return nodedataframe


def IdentiFyBoundaries():
    '''
    Here the keys is to identify the boundaries in the RVE. It will extracts the maximum and the minimum 
    in each coordinate. So, as a consequente, the domain must be a brick.     
    '''

    boundaryEast = max(nodedataframe['X'])
    boundaryWest = min(nodedataframe['X'])
    boundaryNorth = max(nodedataframe['Y'])
    boundarySouth = min(nodedataframe['Y'])
    boundaryUpper = max(nodedataframe['Z'])
    boundaryLower = min(nodedataframe['Z'])

    global RVE_limits

    RVE_limits = {'boundaryEast':boundaryEast,
                  'boundaryWest':boundaryWest,
                  'boundaryNorth':boundaryNorth,
                  'boundarySouth':boundarySouth,
                  'boundaryUpper':boundaryUpper,
                  'boundaryLower':boundaryLower}

    return RVE_limits

'''
There will be 3 groups of nodes:
1)Faces
2)Edges
3)Vertices
Of course, some nodes can be part of the three simultanaly. Therefore, for faces, we have to 
exclude all nodes commom to edges, and for the edges, all nodes commom to vertices. But,
first, we have to select all nodes on boundaries.
'''
def SelecByCood(dataframe,Cood,Value):
    '''
    Function that wil return a sorted dataframe with all rows
    have a commom Cood. 'Cood' is a string ('X','Y'or 'Z') and value
    is a flot
    
    '''
    dataframe_sorted = dataframe.sort_values(by=[Cood]) #Sorting values by the Cood
    dataframe_sorted_boolean_boundary = dataframe_sorted.isin([Value])
    
    indexrows = np.array([])
    
    for i in list(dataframe_sorted_boolean_boundary.index):
        if dataframe_sorted_boolean_boundary.loc[i,Cood]:
            indexrows=np.append(indexrows,int(i)) #obs.: I'vr tried to use list.append, but it didn't work
    
    return dataframe.loc[indexrows]


def FindBoundaryNodes():
    '''
    Given the RVE limits, this method will return all nodes that rely in boundaries. 
    '''
    boundaryWest = RVE_limits['boundaryWest']
    boundaryEast = RVE_limits['boundaryEast']
    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']
    
    west_boundary_nodes = SelecByCood(nodedataframe,'X',boundaryWest)
    east_boundary_nodes = SelecByCood(nodedataframe,'X',boundaryEast)
    north_boundary_nodes = SelecByCood(nodedataframe,'Y',boundaryNorth)
    south_boundary_nodes = SelecByCood(nodedataframe,'Y',boundarySouth)
    upper_boundary_nodes = SelecByCood(nodedataframe,'Z',boundaryUpper)
    lower_boundary_nodes =  SelecByCood(nodedataframe,'Z',boundaryLower)
    
    global nodes_on_boundaries

    nodes_on_boundaries = {'west_boundary_nodes':west_boundary_nodes,
                           'east_boundary_nodes':east_boundary_nodes,
                           'north_boundary_nodes':north_boundary_nodes,
                           'south_boundary_nodes':south_boundary_nodes,
                           'upper_boundary_nodes':upper_boundary_nodes,
                           'lower_boundary_nodes':lower_boundary_nodes}


def TellRVESize():
    '''
    Just a method to return a dictionary with the RVE geometrical sizes
    '''

    west_boundary_nodes = nodes_on_boundaries['west_boundary_nodes']
    east_boundary_nodes = nodes_on_boundaries['east_boundary_nodes']
    north_boundary_nodes = nodes_on_boundaries['north_boundary_nodes']
    south_boundary_nodes = nodes_on_boundaries['south_boundary_nodes']
    upper_boundary_nodes = nodes_on_boundaries['upper_boundary_nodes']
    lower_boundary_nodes =  nodes_on_boundaries['lower_boundary_nodes']


    L = abs(east_boundary_nodes-west_boundary_nodes)
    W = abs(north_boundary_nodes-south_boundary_nodes)
    D = abs(upper_boundary_nodes-lower_boundary_nodes)
    
    GeometricalSizes = {'X':L,'Y':W,'Z':D}
    
    return GeometricalSizes


def FindGeometricalCenter():
    '''
    Just a method to calculate the geometrical center. This is necessary because the position vector 
    must be taken repectively to body geometrical center
    '''
    boundaryWest = RVE_limits['boundaryWest']
    boundaryEast = RVE_limits['boundaryEast']
    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']

    x_c = (boundaryEast+boundaryWest)/2
    y_c = (boundaryNorth+boundarySouth)/2
    z_c = (boundaryUpper+boundaryLower)/2
    
    return x_c,y_c,z_c


def FindGeometricalCenter_dataframe_format():
    '''
    Just a method to return a formatted dataframe with the Geometrical Center of the body. It will be used in the method
    below. 
    '''
    boundaryWest = RVE_limits['boundaryWest']
    boundaryEast = RVE_limits['boundaryEast']
    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']

    x_c = (boundaryEast+boundaryWest)/2
    y_c = (boundaryNorth+boundarySouth)/2
    z_c = (boundaryUpper+boundaryLower)/2
    
    GeoCenter = {'X':x_c,'Y':y_c,'Z':z_c}
    
    return GeoCenter


def GlobalLocalCoodConversion(Cood_input,Arg='To Local'):
    '''
    Makes the conversion between local and global coordinates:    
    here, Cood_input is a line of node datraframe or a dictionary with the following format:
    
    Cood = {'X':X_value,'Y':Y_value,'Z':Z_value}
    
    It is necessary when the RVE is not centered in origin. 
    '''
    
    #Finding Geometrical Center
    GeoCenter = FindGeometricalCenter_dataframe_format()
    
    if Arg == 'To Local':
        
        Cood_local= {'X':None,'Y':None,'Z':None} #Setting up the Cood_local formart
        
        Cood_local['X'] = Cood_input['X']-GeoCenter['X']
        Cood_local['Y'] = Cood_input['Y']-GeoCenter['Y']
        Cood_local['Z'] = Cood_input['Z']-GeoCenter['Z']
        
        return Cood_local
    
    if Arg == 'To Global':
        
        Cood_global= {'X':None,'Y':None,'Z':None} #Setting up the Cood_global formart
        
        Cood_global['X'] = Cood_input['X']+GeoCenter['X']
        Cood_global['Y'] = Cood_input['Y']+GeoCenter['Y']
        Cood_global['Z'] = Cood_input['Z']+GeoCenter['Z']
        
        return Cood_global


def FindGeometricalCenterDataframe(dataframe):
    '''
    A method that returns a geometrical center of a dataframe
    '''
    def set_max_min(dataframeCood):
        '''
        Just a method to returns the minimun and maximum values of a dataframe columun
        '''
        max_value = max(dataframeCood)
        min_value = min(dataframeCood)
        
        return min_value,max_value
    
    x_min,x_max = set_max_min(dataframe['X'])
    y_min,y_max = set_max_min(dataframe['Y'])
    z_min,z_max = set_max_min(dataframe['Z'])
       
    x_c = (x_max+x_min)/2
    y_c = (y_max+y_min)/2
    z_c = (z_max+z_min)/2
    
    return x_c,y_c,z_c

'''
The process will be simple. With boundary group nodes selected, just reselect all nodes on boundary with commom edges,
and create new groups. Further, unselect the nodes of edges that are on boundarys, because they will be the vertices. 

To deal with that role, it will be presented UnselecByCood and SelectInsideSquare
'''
def UnselecByCood(dataframe,Cood,Value):
    '''
    Function that will return a dataframe with all rows that don't have
    a certain cood value. It is, as expected, the opposed of SelecByCood. 
    Here, again Cood is a string and Value is a float. 
    '''
    dataframe_sorted = dataframe.sort_values(by=[Cood]) #Sorting values by the Cood
    dataframe_sorted_boolean_boundary = dataframe_sorted.isin([Value])
    
    indexrows = np.array([])
    
    for i in list(dataframe_sorted_boolean_boundary.index):
        if dataframe_sorted_boolean_boundary.loc[i,Cood]==False:
            indexrows=np.append(indexrows,i) #obs.: I'vr tried to use list.append, but it didn't work
    
    return dataframe.loc[indexrows]


def SelectInsideSquare(center,DataFrame,square_size):
    '''
    Method that will receive a center, which is a dataframe line (important), OR a struct with the follwing keywords:
    center = {'X':Value1,'Y':Value2,'Z':Value3}
    and will return all node index in 'DataFrame'
    that rely inside a square with square_size lenght. In order to do that, this method will calculate 
    an absolute distance abs(a-b) dataframe, and create
    a new dataframe with only nodes with desired coordinates - whith a while loop, which is faster.
    '''
    DataFrameDesiredValues_nodes_to_compare = {'NodeNumber':DataFrame['NodeNumber']}
    DataFrameDesiredValues = pd.DataFrame(data = DataFrameDesiredValues_nodes_to_compare)
    DataFrameDesiredValues.insert(1,'X',center['X'])
    DataFrameDesiredValues.insert(2,'Y',center['Y'])
    DataFrameDesiredValues.insert(3,'Z',center['Z'])
    
    index_for_dataframe = pd.Series(list(DataFrame.index))
    DataFrameDesiredValues = DataFrameDesiredValues.set_index(index_for_dataframe)
    
    subtraction_operation_dataframe = abs(DataFrameDesiredValues.subtract(DataFrame))
    
    comparing_dataframe = pd.DataFrame(data={'NodeNumber':DataFrame['NodeNumber']})
    comparing_dataframe = comparing_dataframe.set_index(index_for_dataframe) #setting index
    
    comparing_dataframe.insert(1,'X',None)
    comparing_dataframe.insert(2,'Y',None)
    comparing_dataframe.insert(3,'Z',None)
    comparing_dataframe.insert(4,'comparing values',None)
    
    comparing_dataframe['X'] = np.where(subtraction_operation_dataframe['X']<square_size/2,True,False)
    comparing_dataframe['Y'] = np.where(subtraction_operation_dataframe['Y']<square_size/2,True,False)
    comparing_dataframe['Z'] = np.where(subtraction_operation_dataframe['Z']<square_size/2,True,False)
    
    comparing_dataframe['comparing values'] = comparing_dataframe.X & comparing_dataframe.Y & comparing_dataframe.Z
    
    comparing_dataframe=comparing_dataframe.sort_values(by='comparing values',ascending=False)
    
    selected_index = np.array([])
        
    index_list = list(comparing_dataframe.index)
    index_i = index_list[0]
    counting_only_trues = 0
    
    while(comparing_dataframe.loc[index_i,'comparing values']):
        selected_index = np.append(selected_index,index_i)
        index_i = index_list[counting_only_trues]
        counting_only_trues=counting_only_trues+1
    
    return selected_index,comparing_dataframe


def FindFaceNodes():
    '''
    Face names follow the same rule as the boundaries names.
    
    The method will identify the nodes that rely on faces exclusively. In order to accomplish the task,
    the methods IdentiFyBoundaries, IdentiFyBoundaries, and UnselecByCood will be used. 
    '''
    
    boundaryWest = RVE_limits['boundaryWest']
    boundaryEast = RVE_limits['boundaryEast']
    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']

    west_boundary_nodes = nodes_on_boundaries['west_boundary_nodes']
    east_boundary_nodes = nodes_on_boundaries['east_boundary_nodes']
    north_boundary_nodes = nodes_on_boundaries['north_boundary_nodes']
    south_boundary_nodes = nodes_on_boundaries['south_boundary_nodes']
    upper_boundary_nodes = nodes_on_boundaries['upper_boundary_nodes']
    lower_boundary_nodes =  nodes_on_boundaries['lower_boundary_nodes']


    Face_west = UnselecByCood(west_boundary_nodes,'Y',boundaryNorth)
    Face_west = UnselecByCood(Face_west,'Y',boundarySouth)
    Face_west = UnselecByCood(Face_west,'Z',boundaryUpper)
    Face_west = UnselecByCood(Face_west,'Z',boundaryLower)

    Face_east = UnselecByCood(east_boundary_nodes,'Y',boundaryNorth)
    Face_east = UnselecByCood(Face_east,'Y',boundarySouth)
    Face_east = UnselecByCood(Face_east,'Z',boundaryUpper)
    Face_east = UnselecByCood(Face_east,'Z',boundaryLower)

    Face_north = UnselecByCood(north_boundary_nodes,'X',boundaryEast)
    Face_north = UnselecByCood(Face_north,'X',boundaryWest)
    Face_north = UnselecByCood(Face_north,'Z',boundaryUpper)
    Face_north = UnselecByCood(Face_north,'Z',boundaryLower)

    Face_south = UnselecByCood(south_boundary_nodes,'X',boundaryEast)
    Face_south = UnselecByCood(Face_south,'X',boundaryWest)
    Face_south = UnselecByCood(Face_south,'Z',boundaryUpper)
    Face_south = UnselecByCood(Face_south,'Z',boundaryLower)

    Face_upper = UnselecByCood(upper_boundary_nodes,'X',boundaryEast)
    Face_upper = UnselecByCood(Face_upper,'X',boundaryWest)
    Face_upper = UnselecByCood(Face_upper,'Y',boundaryNorth)
    Face_upper = UnselecByCood(Face_upper,'Y',boundarySouth)

    Face_lower = UnselecByCood(lower_boundary_nodes,'X',boundaryEast)
    Face_lower = UnselecByCood(Face_lower,'X',boundaryWest)
    Face_lower = UnselecByCood(Face_lower,'Y',boundaryNorth)
    Face_lower = UnselecByCood(Face_lower,'Y',boundarySouth)

    global only_face_nodes

    only_face_nodes = { 'Face_west':Face_west,
                        'Face_east':Face_east,
                        'Face_north':Face_north,
                        'Face_south':Face_south,
                        'Face_upper':Face_upper,
                        'Face_lower':Face_lower
                      }


def FindEdgesNodes():
    '''
    Method to selected the Nodes in the Edges.

    Obs: The edges names follow the right hand rule, beggining in x positive or x-y positive. 
    '''

    boundaryWest = RVE_limits['boundaryWest']
    boundaryEast = RVE_limits['boundaryEast']
    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']

    west_boundary_nodes = nodes_on_boundaries['west_boundary_nodes']
    east_boundary_nodes = nodes_on_boundaries['east_boundary_nodes']
    north_boundary_nodes = nodes_on_boundaries['north_boundary_nodes']
    south_boundary_nodes = nodes_on_boundaries['south_boundary_nodes']

    E_a = SelecByCood(east_boundary_nodes,'Z',boundaryLower)
    E_a = UnselecByCood(E_a,'Y',boundaryNorth)
    E_a = UnselecByCood(E_a,'Y',boundarySouth)

    E_b = SelecByCood(north_boundary_nodes,'Z',boundaryLower)
    E_b = UnselecByCood(E_b,'X',boundaryEast)
    E_b = UnselecByCood(E_b,'X',boundaryWest)

    E_c = SelecByCood(west_boundary_nodes,'Z',boundaryLower)
    E_c = UnselecByCood(E_c,'Y',boundaryNorth)
    E_c = UnselecByCood(E_c,'Y',boundarySouth)

    E_d = SelecByCood(south_boundary_nodes,'Z',boundaryLower)
    E_d = UnselecByCood(E_d,'X',boundaryEast)
    E_d = UnselecByCood(E_d,'X',boundaryWest)

    E_e = SelecByCood(east_boundary_nodes,'Y',boundaryNorth)
    E_e = UnselecByCood(E_e,'Z',boundaryUpper)
    E_e = UnselecByCood(E_e,'Z',boundaryLower)

    E_f = SelecByCood(west_boundary_nodes,'Y',boundaryNorth)
    E_f = UnselecByCood(E_f,'Z',boundaryUpper)
    E_f = UnselecByCood(E_f,'Z',boundaryLower)

    E_g = SelecByCood(west_boundary_nodes,'Y',boundarySouth)
    E_g = UnselecByCood(E_g,'Z',boundaryUpper)
    E_g = UnselecByCood(E_g,'Z',boundaryLower)

    E_h = SelecByCood(east_boundary_nodes,'Y',boundarySouth)
    E_h = UnselecByCood(E_h,'Z',boundaryUpper)
    E_h = UnselecByCood(E_h,'Z',boundaryLower)

    E_i = SelecByCood(east_boundary_nodes,'Z',boundaryUpper)
    E_i = UnselecByCood(E_i,'Y',boundaryNorth)
    E_i = UnselecByCood(E_i,'Y',boundarySouth)

    E_j = SelecByCood(north_boundary_nodes,'Z',boundaryUpper)
    E_j = UnselecByCood(E_j,'X',boundaryEast)
    E_j = UnselecByCood(E_j,'X',boundaryWest)

    E_k = SelecByCood(west_boundary_nodes,'Z',boundaryUpper)
    E_k = UnselecByCood(E_k,'Y',boundaryNorth)
    E_k = UnselecByCood(E_k,'Y',boundarySouth)

    E_l = SelecByCood(south_boundary_nodes,'Z',boundaryUpper)
    E_l = UnselecByCood(E_l,'X',boundaryWest)
    E_l = UnselecByCood(E_l,'X',boundaryEast)
    
    global only_edge_nodes

    only_edge_nodes = {
        
        'E_a':E_a,
        'E_b':E_b,
        'E_c':E_c,
        'E_d':E_d,
        'E_e':E_e,
        'E_f':E_f,
        'E_g':E_g,
        'E_h':E_h,
        'E_i':E_i,
        'E_j':E_j,
        'E_k':E_k,
        'E_l':E_l
    }
    

def FindVerticesNodes():
    '''
    A method to define edges nodes.
    
    The vertices names follow the right-hand rule, begging at x-y positive quadrant.
    '''
    
    west_boundary_nodes = nodes_on_boundaries['west_boundary_nodes']
    east_boundary_nodes = nodes_on_boundaries['east_boundary_nodes']

    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']


    v_a = SelecByCood(east_boundary_nodes,'Z',boundaryLower)
    v_a = SelecByCood(v_a,'Y',boundaryNorth)

    v_d = SelecByCood(east_boundary_nodes,'Z',boundaryLower)
    v_d = SelecByCood(v_d,'Y',boundarySouth)

    v_b = SelecByCood(west_boundary_nodes,'Z',boundaryLower)
    v_b = SelecByCood(v_b,'Y',boundaryNorth)

    v_c = SelecByCood(west_boundary_nodes,'Z',boundaryLower)
    v_c = SelecByCood(v_c,'Y',boundarySouth)

    v_e = SelecByCood(east_boundary_nodes,'Z',boundaryUpper)
    v_e = SelecByCood(v_e,'Y',boundaryNorth)

    v_h = SelecByCood(east_boundary_nodes,'Z',boundaryUpper)
    v_h = SelecByCood(v_h,'Y',boundarySouth)

    v_f = SelecByCood(west_boundary_nodes,'Z',boundaryUpper)
    v_f = SelecByCood(v_f,'Y',boundaryNorth)

    v_g = SelecByCood(west_boundary_nodes,'Z',boundaryUpper)
    v_g = SelecByCood(v_g,'Y',boundarySouth)
    
    global only_vertices_nodes

    only_vertices_nodes = {
                            'v_a':v_a,
                            'v_d':v_d,
                            'v_b':v_b,
                            'v_c':v_c,
                            'v_e':v_e,
                            'v_h':v_h,
                            'v_f':v_f,
                            'v_g':v_g
                          }

'''
The stragy here is to find, in the opposite face, the node pair, and save the node pairs in a dataframe, 
by the notation (-x,y,z), for example. The best practice is to define a method for it. 
The search will be done opposite dataframe. That is, the node pairs of Face_east will be search in the Face_west,
which assures less work and better results. 
'''
def ReturnKeyWordsAslist(dictionary):
    '''
    Method to return a list with all dictionary KeysWords
    '''
    return list(dictionary.keys())


def DictEntities():
    '''
    As is a little bit tedious to write all the entitie names again, this method
    will return a dictionary where All KeyWords connect with it respective variable.
    Also, one can do a loop between this variables and its pairs.
    '''

    DictEntities = {
        
        'Face_east':only_face_nodes['Face_east'],
        'Face_north':only_face_nodes['Face_north'],
        'Face_upper':only_face_nodes['Face_upper'],
        'E_a':only_edge_nodes['E_a'],
        'E_b':only_edge_nodes['E_b'],
        'E_c':only_edge_nodes['E_c'],
        'E_d':only_edge_nodes['E_d'],
        'E_e':only_edge_nodes['E_e'],
        'E_f':only_edge_nodes['E_f'],
        'v_a':only_vertices_nodes['v_a'],
        'v_b':only_vertices_nodes['v_b'],
        'v_c':only_vertices_nodes['v_c'],
        'v_d':only_vertices_nodes['v_d']
    } 

    return DictEntities,ReturnKeyWordsAslist(DictEntities)


def TellPairVar(EntityMasterName):
    '''
    Choosing the entities to be paried is very prone to error.  Therefore, this method will return a dictionary with
    a par entity.
    
    '''

    # Dict_pairs_strings = {
    #     'Face_east':Face_west,
    #     'Face_north':Face_south,
    #     'Face_upper':Face_lower,
    #     'E_a':E_k,
    #     'E_b':E_l,
    #     'E_c':E_i,
    #     'E_d':E_j,
    #     'E_e':E_g,
    #     'E_f':E_h,
    #     'v_a':v_g,
    #     'v_b':v_h,
    #     'v_c':v_e,
    #     'v_d':v_f
    # }

    Dict_pairs_strings = {
        'Face_east':only_face_nodes['Face_west'],
        'Face_north':only_face_nodes['Face_south'],
        'Face_upper':only_face_nodes['Face_lower'],
        'E_a':only_edge_nodes['E_k'],
        'E_b':only_edge_nodes['E_l'],
        'E_c':only_edge_nodes['E_i'],
        'E_d':only_edge_nodes['E_j'],
        'E_e':only_edge_nodes['E_g'],
        'E_f':only_edge_nodes['E_h'],
        'v_a':only_vertices_nodes['v_g'],
        'v_b':only_vertices_nodes['v_h'],
        'v_c':only_vertices_nodes['v_e'],
        'v_d':only_vertices_nodes['v_f']
    }

    
    return Dict_pairs_strings[EntityMasterName]
    

def ChooseCoodToReflect(EntityMasterName):
    '''
    Method to choose the correct Coordinate to Reflect. Is basic a dictionary, where
    each keyword has and Cood do Reflect
    '''
    
    DictionaryCood = {
        
        'Face_east':['X'],
        'Face_north':['Y'],
        'Face_upper':['Z'],
        'E_a':['X','Z'],
        'E_b':['Y','Z'],
        'E_c':['X','Z'],
        'E_d':['Y','Z'],
        'E_e':['X','Y'],
        'E_f':['X','Y'],   
        'v_a':None,
        'v_b':None,
        'v_c':None,
        'v_d':None
    }
    
    return DictionaryCood[EntityMasterName]


def ChooseTypeEntity(EntityMasterName):
    '''
    Method that will return the entity type. Returns a string
    '''
    DictionaryCood = {
        
        'Face_east':'Face',
        'Face_north':'Face',
        'Face_upper':'Face',
        'E_a':'Edge',
        'E_b':'Edge',
        'E_c':'Edge',
        'E_d':'Edge',
        'E_e':'Edge',
        'E_f':'Edge',
        'v_a':'vertice',
        'v_b':'vertice',
        'v_c':'vertice',
        'v_d':'vertice'
    }

    return DictionaryCood[EntityMasterName]


def ListRegionNumbers():
    '''
    Just a method to return a list with all Geometry regions
    '''
    Regions = []
    for i in range(1,14):
        Regions_name = "Region{}".format(i)
        Regions.append(Regions_name)
 
    return Regions


def ChooseRegion(Index):
    '''
    Just a method to choose the Region
    '''
    Regions = ListRegionNumbers()

    return Regions[Index]


def ChooseEntityName(EntityType):
    '''
    Method that will return the entity name, given an entity type. It is the inverse function of
    ChooseTypeEntity()
    '''
    Dictionary_Entityname = {
        
        'Region1':'Face_east',
        'Region2':'Face_north',
        'Region3':'Face_upper',
        'Region4':'E_a',
        'Region5':'E_b',
        'Region6':'E_c',
        'Region7':'E_d',
        'Region8':'E_e',
        'Region9':'E_f',
        'Region10':'v_a',
        'Region11':'v_b',
        'Region12':'v_c',
        'Region13':'v_d'
    }

    return Dictionary_Entityname[EntityType]


def FindClosestNodeV2(i_node,dataframeOppositeCutted):
    '''
    New method to find the closest node. Again, for each node, the task here is to calculate de least euclidean distance. 
    The diference here, is that instead take all dataframeOpposite nodes, it will look the search in a square, and the proceeding 
    will be based in 7 operations:
    a)Create a dataframe with identical to dataframeOppositeCutted, but with all 'X', 'Y' and 'Z' equals to i_node x,y, and z
    b)Element-wise subtraction between i_node dataframe and dataframeOppositeCutted
    c)takes the abs() value of this subtraction
    d)sums the subtraction over x,y,z
    e)re-order the resulting dataframe in ascending order
    f)Takes the first position
    '''
    
    #Create i_node dataframe
    i_node_x = i_node['X']
    i_node_y = i_node['Y']
    i_node_z = i_node['Z']
    
    index_for_dataframe = pd.Series(list(dataframeOppositeCutted.index))
    i_node_df = pd.DataFrame(data={'NodeNumber':dataframeOppositeCutted['NodeNumber']})
    i_node_df = i_node_df.set_index(index_for_dataframe) #setting index
    
    i_node_df.insert(1,'X',i_node_x)
    i_node_df.insert(2,'Y',i_node_y)
    i_node_df.insert(3,'Z',i_node_z)
    
    #Element wise subtraction and take abs value
    
    subtraction_operation_dataframe = abs(i_node_df.subtract(dataframeOppositeCutted))
    
    #Sum in colum axis
    sum_over_subtraction_dataframe = subtraction_operation_dataframe.sum(axis=1)
    
    #sort and Take the first least value
    least = sum_over_subtraction_dataframe.nsmallest(n=1)
    
    return least.index


def FindPairs(dataframe,dataframeOpposite,CoodToReflect):
    '''
    Method that will receive a dataframe with coordinates, and a cood. to be reflected. 
    Therefore, if it receives 'X', it will seeks for (-X,Y,Z) in the other dataframe. 
    CoodToReflect is a string. 
    It returns the index of the dataframe that contain the paired nodes. 
    '''
    IndexOfOppositeDataframeList = np.array([])
    '''
    In order to avoid bug, as the node index pair is found, the originary node index will be stored. 
    This is just for security. This is will stored in 'Index_dataframe_master' variable
    '''
    Index_dataframe_master = np.array([])
    '''
    The process will be simple:
        1) Get the i-esim coordinate of the dataframe
        2) find the opposed supposed node coordinate:
            2.a)Convert the i-esim coordinate to local CS
            2.b)Reflect the desired coordinates in local CS
            2.c)Get back to Global Coordinate System
        4) Get the node index by it Coordinate
    '''
    
    for node_in_dataframe in dataframe.index:
        '''
        Here, I am invertig the requested coordinate
        '''
        #Getting the i-esim node coordinate
        CurrentNodeCoordinate = GetCoodByIndex(dataframe,node_in_dataframe)
        #Converting to local Coordinates
        CurrentNodeCoordinate_local = GlobalLocalCoodConversion(CurrentNodeCoordinate,'To Local')
        #Reflecting Coordinate
        CurrentNodeCoordinate_local[CoodToReflect[0]] = -CurrentNodeCoordinate_local[CoodToReflect[0]]
        #Getting Back to original CS
        CurrentNodeCoordinate_global_reflected =  GlobalLocalCoodConversion(CurrentNodeCoordinate_local,'To Global')
        #Getting the node index in opposite dataframe
        IndexOfOppositeDataframe = GetIndexByCood(dataframeOpposite,CurrentNodeCoordinate_global_reflected)
        IndexOfOppositeDataframeList = np.append(IndexOfOppositeDataframeList,IndexOfOppositeDataframe)
        Index_dataframe_master = np.append(Index_dataframe_master,node_in_dataframe)
    

    #
    return Index_dataframe_master,IndexOfOppositeDataframeList


def FindEdgesPairs(dataframe,dataframeOpposite,CoodToReflect):
    '''
    Method to find diagonally opposed pair of nodes in edges. 
    '''
    IndexOfOppositeDataframeList = np.array([])
    Index_dataframe_master = np.array([])
    
    '''
    The process will be simple:
        1) Get the i-esim coordinate of the dataframe
        2) find the opposed supposed node coordinate:
            2.a)Convert the i-esim coordinate to local CS
            2.b)Reflect the desired coordinates in local CS
            2.c)Get back to Global Coordinate System
        4) Get the node index by it Coordinate
    '''
    #print("Searching for paired nodes in Edges")
    for node_in_dataframe in dataframe.index:
        
        #Getting the i-esim node coordinate
        CurrentNodeCoordinate = GetCoodByIndex(dataframe,node_in_dataframe)
        #Converting to local Coordinates
        CurrentNodeCoordinate_local = GlobalLocalCoodConversion(CurrentNodeCoordinate,'To Local')
        #Reflecting Coordinate
        CurrentNodeCoordinate_local[CoodToReflect[0]] = -CurrentNodeCoordinate_local[CoodToReflect[0]]
        CurrentNodeCoordinate_local[CoodToReflect[1]] = -CurrentNodeCoordinate_local[CoodToReflect[1]]
        #Getting Back to original CS
        CurrentNodeCoordinate_global_reflected =  GlobalLocalCoodConversion(CurrentNodeCoordinate_local,'To Global')
        #Getting the node index in opposite dataframe
        IndexOfOppositeDataframe = GetIndexByCood(dataframeOpposite,CurrentNodeCoordinate_global_reflected)
        IndexOfOppositeDataframeList = np.append(IndexOfOppositeDataframeList,IndexOfOppositeDataframe)
        Index_dataframe_master = np.append(Index_dataframe_master,node_in_dataframe)

    return Index_dataframe_master,IndexOfOppositeDataframeList


def FindVerticePairs(dataframe,dataframeOpposite):
    '''
    Method that will just return the opposite vertices dataframe index. As there is only one
    node on vertice, the dataframe and dataframeOpposite ALREADY ARE the pairs nodes.
    So, the deal here is trivial, it is just return this dataframe index. 
    '''
    IndexOfMasterDataframeList = list(dataframe.index)
    IndexOfOppositeDataframeList = list(dataframeOpposite.index)
    
    return IndexOfMasterDataframeList,IndexOfOppositeDataframeList
'''
Now we need to find the node pairs to apply PBC. For that, it will defined a method that return the
dataframe row index of a coordinate point passed.
Further, we need function that return the coordinates for a given dataframe index
'''
def GetIndexByCood(dataframe,Cood):
    '''
    Method that receive a dataframe, and a Cood, and check if the exact Cood. exists in dataframe,
    returning it index.
    Cood actually is a dataframe where contains just the information of a specific node.
    For opmization sakes, the nodes in dataframe will be reselected. 
    '''
    original_dataframe = dataframe
    index_nodes_selected,comparison_dataframe = SelectInsideSquare(Cood,dataframe,tol_global)
    
    #reselecting dataframe
    dataframe = dataframe.loc[index_nodes_selected]
    
    if dataframe.shape[0]<1:
        print("----------------------------------")
        print("Original Dataframe to Find node:")
        print(original_dataframe)
        print("Supposed Existing Cood:")
        print(Cood)
        print("Any Node Select")
        print("Check if the mesh is periodic, or set the tolerance by setTOL Command")
        print(dataframe)
        input("Press Enter to Continue")
   
    if len(index_nodes_selected)==1:
         #If in index_nodes_selected list has only one node, this is the paired node
        return index_nodes_selected
    
    else:
        #Calls FindClosestNodeV2
        return FindClosestNodeV2(i_node=Cood,dataframeOppositeCutted=dataframe)


def CreateDictWithCoodList(List):
    '''
    Method that will receive a list, for example, a list
    with coordinates, and will return a dict
    '''
    dictionary = {'X':List[0],
                  'Y':List[1],
                  'Z':List[2]}
    return dictionary   


def GetCoodByIndex(dataframe,Index):
    '''
    Function that will returns a dictionary with keywords
    NodeNumber,X,Y,Z, and with them respective values
    '''
    if Index in list(dataframe.index):
        
        dataframe_index_list = dataframe.loc[Index]
        
        dictionary_cood = {'NodeNumber':dataframe_index_list['NodeNumber'],
                      'X':dataframe_index_list['X'],
                      'Y':dataframe_index_list['Y'],
                      'Z':dataframe_index_list['Z']}
        return dictionary_cood
    else:
        return 'ERROR: Such Index doesnt exist in the dataframe'


def CreatePairedNodesDataframe(DataframeMaster,DataframeSlave,MasterList,SlaveList,EntityName):
    '''
    Method that take the two paried dataframes (that come from above methods), and create a list with
    the paired nodes, in order to apply PBC conditions.
    DataframeMaster: Dataframe of the master nodes information
    DataframeSlate: Dataframe of the slave nodes information
    
    '''
    ColumnMaster = list(DataframeMaster.loc[MasterList,'NodeNumber'])
    ColumnSlave = list(DataframeSlave.loc[SlaveList,'NodeNumber'])
    data = {'Node Master':ColumnMaster,
            'Node Slave':ColumnSlave,
            'EntityName':EntityName}

    dataframe = pd.DataFrame(data=data)

    dataframe=dataframe.set_index('EntityName')

    return dataframe


def StrainState(Strain,Const):
    '''
    Method that will return a strain State, as a Matrix.
    Const is the Strain you want to impose in body
    '''
    Exx = np.array([[Const,0,0],
                   [0,0,0],
                   [0,0,0]])
    
    Eyy = np.array([[0,0,0],
                   [0,Const,0],
                   [0,0,0]])
    
    Ezz = np.array([[0,0,0],
                   [0,0,0],
                   [0,0,Const]])
    
    Exy = np.array([[0,Const,0],
                   [Const,0,0],
                   [0,0,0]])
    
    Eyz = np.array([[0,0,0],
                   [0,0,Const],
                   [0,Const,0]])
    
    Exz = np.array([[0,0,Const],
                   [0,0,0],
                   [Const,0,0]])
    
    DictionaryStrain = {'Exx':Exx,
                        'Eyy':Eyy,
                        'Ezz':Ezz,
                        'Exy':Exy,
                        'Eyz':Eyz,
                        'Exz':Exz
                       }
    
    return DictionaryStrain[Strain]


def StrainCasesList():
    '''
    Just a method to return a list with the strain case (To be used in a loop). Yes, it is a little dumb,
    I've tried tu return 'DictionaryStrain' in StrainState method, but it lead to some erros, so I decided to be a little bit
    redundant here.
    '''
    DictionaryList = ['Exx','Eyy','Ezz','Exy','Eyz','Exz']
    
    return DictionaryList


def PBC_apdl_commands(PairedNodes,StrainState,Normal,EntityMasterName,EntityType):
    '''
    The PBC needs paried nodes to be applied. On faces, it is a relatively eazy task: just take opposed nodes on face and
    apply the constrained equatios. But on edges and vertices theres come a problem: that is a discontinous point. It would be
    like the same point would receive simultanely two constrained equations.  Further, to assure equilibruim in body
    it must be taken diagonnaly oppossed edges and vertices  - therefore, a center of equilibruim
    occurs in the GC of the body(it is a way to see in understand it.). 
    Following, a just explanation of the normals will be made. a1,a2, and a3 are coordinates; further, 
    a1 is the boundaryEast, a2 is the boundaryNorth, and a3 is the boundaryUpper of this code. 
    -For faces, the position vector will be a vector centered in face (to justify it, see LUCIANO article), which, for example, becomes
    [a1,0,0].
    -For edges, the treatment will be a compound vector, v = ([a1,0,0]+[0,a2,0])=[a1,a2,0], depending of the case, of course. This assures the constraints
    equations match with continuity displacement of the body. 
    -For vertices, analogously, the normal will be a combination, becoming v = [a1,a2,a3]
    
    Finally, a explantion of the input variabels:
    PariedNodes is a dataframe with node number of paired nodes (the return of 'CreatePairedNodesDataframe' Method.)
    StrainCase is a matrix with the desired StrainState (just the return of 'StrainState' method)
    Normal is the normal (or the equivalent, for edges and vertices) where you will apply the condition; on faces,
    edges or vertices. 
    '''
    f = open('PBC_CE_Commands.tmp','w')
    
    u = ['UX','UY','UZ']
    
    '''
    Matrix multiplication
    '''
    
    beta = 2*StrainState.dot(Normal)

    f.write('\n!------------------------------------------!\n')
    f.write('!Writing CE for {}'.format(EntityMasterName))
    f.write('\n!------------------------------------------!\n')

    if EntityType in list(['Face','Edge']):

        Node_Master_colum = list(PairedNodes['Node Master'])
        Node_Slave_colum = list(PairedNodes['Node Slave'])
        paired_node_length = len(Node_Master_colum) #It could be len(Node_Slave_colum)
        
        for i in range(0,paired_node_length):
            #Selecting Paired nodes
            Node_Master = Node_Master_colum[i]
            Node_Slave  = Node_Slave_colum[i]
            for j in range(StrainState.shape[0]):
                                
                command = "CE,NEXT,{},{},{},1,{},{},-1".format(float(beta[j]),
                                                            Node_Master,
                                                                u[j],
                                                            Node_Slave,
                                                                u[j])
                f.write("\n{}".format(command))
                
    if EntityType == 'vertice':

        Node_Master = PairedNodes['Node Master']
        Node_Slave  = PairedNodes['Node Slave']

        for j in range(StrainState.shape[0]):

            command_node_master = "D,{},{},{}".format(Node_Master,
                                                    u[j],
                                                    float(beta[j]/2))
            command_node_slave = "D,{},{},{}".format(Node_Slave,
                                                    u[j],
                                                    float(-beta[j]/2))
            
            f.write("\n{}".format(command_node_master))
            f.write("\n{}".format(command_node_slave))
    
    f.close()


def PariedNodesOfEntities(Entity,Master,Slave,Cood,EntityName):
    '''
    As the process is repetitive, this method aims to avoid operation error. Here, 
    Master is the face/edge/vertice where the master nodes are located,
    and Slave is the opposite face/edge/vertice where the slave node are located. 
    Cood is a list of strings with the Coordinate to reflect, ex: ['X','Y']
    It returns a dataframe
    '''
    if Entity == 'Face':
        MasterList,SlaveList = FindPairs(Master,Slave,Cood)
    if Entity =='Edge':
        MasterList,SlaveList = FindEdgesPairs(Master,Slave,Cood)
    if Entity =='vertice':
        MasterList,SlaveList = FindVerticePairs(Master,Slave)

    DataframePairedNodes = CreatePairedNodesDataframe(Master,Slave,MasterList,SlaveList,EntityName)
    
    return DataframePairedNodes


def ChoosePositionVector(EntityName):
    '''
    Method that will return the position vector of each Face/Edge/Vertice 
    '''

    boundaryWest = RVE_limits['boundaryWest']
    boundaryEast = RVE_limits['boundaryEast']
    boundaryNorth = RVE_limits['boundaryNorth']
    boundarySouth = RVE_limits['boundarySouth']
    boundaryUpper = RVE_limits['boundaryUpper']
    boundaryLower = RVE_limits['boundaryLower']

    
    x_c,y_c,z_c = FindGeometricalCenter()
    
    v1 = np.zeros((3,1)) #Position Vector for East face
    v1[0]=boundaryEast -x_c
    v1[1]=0

    v2 = np.zeros((3,1)) #Position Vector for North face
    v2[0]=0
    v2[1]=boundaryNorth -y_c
    v2[2]=0

    v3 = np.zeros((3,1)) #Position vector for Upper face
    v3[0]=0
    v3[1]=0
    v3[2]=boundaryUpper -z_c
    v4 = np.zeros((3,1)) #Equivalent position vector for E_a edge
    v4[0]=boundaryEast -x_c
    v4[1]=0
    v4[2]=boundaryLower -z_c
    v5 = np.zeros((3,1)) #Equivalent position vector for E_a edge
    v5[0]=0
    v5[1]=boundaryNorth -y_c
    v5[2]=boundaryLower -z_c
    v6 = np.zeros((3,1)) #Equivalent position vector for E_c edge
    v6[0]=boundaryWest -x_c
    v6[1]=0
    v6[2]=boundaryLower -z_c
    v7 = np.zeros((3,1)) #Equivalent position vector for E_d edge
    v7[0]=0
    v7[1]=boundarySouth -y_c
    v7[2]=boundaryLower -z_c
    v8 = np.zeros((3,1)) #Equivalent position vector for E_e edge 
    v8[0]=boundaryEast -x_c
    v8[1]=boundaryNorth -y_c
    v8[2]=0
    v9 = np.zeros((3,1)) #Equivalent position vector for E_f edge 
    v9[0]=boundaryWest -x_c
    v9[1]=boundaryNorth -y_c
    v9[2]=0
    v10 = np.zeros((3,1)) # Equivalent position vector for v_a vertice
    v10[0]=boundaryEast -x_c
    v10[1]=boundaryNorth -y_c
    v10[2]=boundaryLower -z_c
    v11 = np.zeros((3,1)) # Equivalent position vector for v_b vertice
    v11[0]=boundaryWest -x_c
    v11[1]=boundaryNorth -y_c
    v11[2]=boundaryLower -z_c
    v12 = np.zeros((3,1)) # Equivalent position vector for v_c vertice
    v12[0]=boundaryWest -x_c
    v12[1]=boundarySouth -y_c
    v12[2]=boundaryLower -z_c
    v13 = np.zeros((3,1)) #Equivalent position vector for v_d vertice
    v13[0]=boundaryEast -x_c
    v13[1]=boundarySouth -y_c
    v13[2]=boundaryLower -z_c
    
    PositionVectorDictionary = {
        
        'Face_east':v1,
        'Face_north':v2,
        'Face_upper':v3,
        'E_a':v4,
        'E_b':v5,
        'E_c':v6,
        'E_d':v7,
        'E_e':v8,
        'E_f':v9,
        'v_a':v10,
        'v_b':v11,
        'v_c':v12,
        'v_d':v13
        
    }
    
    return PositionVectorDictionary[EntityName]


def apdl_commands_extract_export_results(path,case):

    directory = path

    f = open("commands_for_save.tmp","w")
    #print("Saving commands to extract ANSYS results")

    f.write('\n!-------------------------------------!')
    f.write('\n!EXTRACTING STRESS AND STRAINS RESULTS')
    f.write('\n/POST1')
    #f.write('\nESEL, S, ENAME, , 185 !Select only the volume elements ')
    f.write("\nESEL,ALL")
    f.write('\n*get,elementnumber,elem,,count !Get the maximum number of element')
    f.write('\n*dim,volu_stress_strain,array,elementnumber, 13! Creates a array with n rows and 13 columns')
    f.write('\n*dim,volumelist,array,elementnumber, 1! Creates a array with "elementnumber" rows and 1 columns')
    f.write('\n*VGET,volumelist(1,1),elem, , elist !Commando to get the element numbers')
    f.write('\n\n!Making a loop to get the volume of each element:')
    f.write('\n*DO,volusave,1,elementnumber,1')
    f.write('\n*GET,elvol,ELEM,volumelist(volusave,1),VOLU')
    f.write('\n*SET,volu_stress_strain(volusave,1),elvol')
    f.write('\n*ENDDO')
    f.write('\n\n!Table to store stress results')
    f.write('\nETABLE,sxx,S,X')
    f.write('\nETABLE,syy,S,Y')
    f.write('\nETABLE,szz,S,Z')
    f.write('\nETABLE,sxy,S,XY')
    f.write('\nETABLE,syz,S,YZ')
    f.write('\nETABLE,sxz,S,XZ')
    f.write('\n\n')
    f.write('\n!Assign stress on variables:\n')
    f.write('\n*vget,volu_stress_strain(1,2),elem,,etab,sxx')
    f.write('\n*vget,volu_stress_strain(1,3),elem,,etab,syy')
    f.write('\n*vget,volu_stress_strain(1,4),elem,,etab,szz')
    f.write('\n*vget,volu_stress_strain(1,5),elem,,etab,sxy')
    f.write('\n*vget,volu_stress_strain(1,6),elem,,etab,syz')
    f.write('\n*vget,volu_stress_strain(1,7),elem,,etab,sxz')
    f.write('\n')
    f.write('\n!Creating table with strains results:')
    f.write('\nETABLE,exx,EPEL,X')
    f.write('\nETABLE,eyy,EPEL,Y ')
    f.write('\nETABLE,ezz,EPEL,Z')
    f.write('\nETABLE,exy,EPEL,XY')
    f.write('\nETABLE,eyz,EPEL,YZ')
    f.write('\nETABLE,exz,EPEL,XZ')
    f.write('\n!Assign strain on variables:\n')
    f.write('\n*vget,volu_stress_strain(1,8),elem,,etab,exx')
    f.write('\n*vget,volu_stress_strain(1,9),elem,,etab,eyy')
    f.write('\n*vget,volu_stress_strain(1,10),elem,,etab,ezz')
    f.write('\n*vget,volu_stress_strain(1,11),elem,,etab,exy')
    f.write('\n*vget,volu_stress_strain(1,12),elem,,etab,eyz')
    f.write('\n*vget,volu_stress_strain(1,13),elem,,etab,exz')

    f.write('\n!Commands to save in arquive')

    #----------------------------------------------------------------

    f.write("\n*CREATE,macrotowrite")
    f.write("\n*CFOPEN,'{}\\stressresults{}',temp,' '".format(directory,case))
    f.write("\n*VWRITE,'#Element',',','VOL',',','SXX',',','SYY',',','SZZ',',','SXY',',','SYZ',',','SXZ'")
    f.write("\n(2x,a9,a1,a3,a1,a3,a1,a3,a1,a3,a1,a3,a1,a3,a1,a3)")
    f.write("\n*VWRITE,volumelist(1,1),',',volu_stress_strain(1,1),',',volu_stress_strain(1,2),',',volu_stress_strain(1,3),',',volu_stress_strain(1,4),',',volu_stress_strain(1,5),',',volu_stress_strain(1,6),',',volu_stress_strain(1,7)")
    f.write("\n(2x,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7)")
    f.write('\n*CFCLOS')

    f.write("\n*CFOPEN,'{}\\strainresults{}',temp,' '".format(directory,case))
    f.write("\n*VWRITE,'#Element',',','VOL',',','EXX',',','EYY',',','EZZ',',','EXY',',','EYZ',',','EXZ'")
    f.write("\n(2x,a9,a1,a3,a1,a3,a1,a3,a1,a3,a1,a3,a1,a3,a1,a3)")
    f.write("\n*VWRITE,volumelist(1,1),',',volu_stress_strain(1,1),',',volu_stress_strain(1,8),',',volu_stress_strain(1,9),',',volu_stress_strain(1,10),',',volu_stress_strain(1,11),',',volu_stress_strain(1,12),',',volu_stress_strain(1,13)")
    f.write("\n(2x,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7,a1,E14.7)")
    f.write('\n*CFCLOS')
    f.write('\n*END')
    f.write('\n/INPUT,macrotowrite ')
    
    f.close()
    
    return None


def SaveAverageResults(StrainDictionary,StressDictionary,StressState,StrainAverage,StressAverage):
    '''
    Method that will receive two dictionaries, being them the average streesses of each case. 
    At each iteration, a keyword (namely, StressState) will be added, in order to save the results. 
    '''
    
    StrainDictionary[StressState]=StrainAverage
    StressDictionary[StressState]=StressAverage
        
    return StrainDictionary,StressDictionary


def TellsDate():
    '''
    Method to tells the date. Returns a string
    '''
    import datetime

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    return date


def TellsCurrentDirectory():
    '''
    A method to tell the current directory
    '''
    import os
    directory = os.getcwd()
    return directory


def DefaultSeperatorTerminal():
    '''
    Just a method to print a default separator in Terminal
    '''
    print("\n!------------------------------------------------!\n")

    return None


def DeleteTempFiles():
    '''
    A macro to delete the tempory files generated during the execution. 
    '''
    import os
    os.remove('PBC_CE_for_strain_case.tmp')
    os.remove('PBC_CE_Commands.tmp')
    os.remove('nodecood.tmp')
    os.remove('commands_for_save.tmp')

    return None


def CheckIfFolderExists(folder_to_check):
    '''
    Method that will receive a folder path, and check if it exists. If don't, create it
    '''
    import os
    if not os.path.exists(folder_to_check):
        os.makedirs(folder_to_check)

    return os.path.exists(folder_to_check)


class PeriodicCommandSetup():
    '''
    Class which will define some constant parameters in the analisys.
    The most important thing here is to create the paired node dataframe.

    OBS.: The geomacrome name comes without extension!
    Therefore, put 'anything' and NOT 'anything.cdb'
    '''

    def __init__(self,geomacroname='Default',geomacro_folder='Default',tol=0.0001):

        #global macroname_global,macro_folder_global

        DefaultSeperatorTerminal()
        print("         Starting the PBC Applying")
        DefaultSeperatorTerminal()
        
        if geomacro_folder == 'Default':
            geomacro_folder = r"{}\CDB Files".format(TellsCurrentDirectory())
            CheckIfFolderExists(geomacro_folder)
            if not CheckIfFolderExists(geomacro_folder):
                print(r"Creating a ..\CDB Files Directory. Put all CDB's there, for best practices. But, the program still works otherway.")
                geomacro_folder = r"{}".format(TellsCurrentDirectory())
            '''
            The last lines are kind confusing. But here it goes some explanation: Fist, it checks if the Folder \CDB File exists. If not, the folder is created. 
            Then, if the folder doens't exists, a warning message appears. But, even if the folder doesn't exists, the program will search for the file in the current folder.
            '''
                
        if geomacroname == 'Default':
            geomacroname='geo_macro_created'

        #Getting the folder and file to be working in
        self.macroname = geomacroname 
        self.geomacro_folder = geomacro_folder
        self.tol = SetTOL(tol)

        # Executing the primordial methods
        self.nodedata = GetNodeDataFromCDB(macro_folder=geomacro_folder,cdbname=geomacroname)
        self.nodedataframe = CreatDataframeFromNodeData(self.nodedata)
        self.RVE_limits = IdentiFyBoundaries()
        # Set Some global vars
        FindBoundaryNodes() 
        FindFaceNodes()
        FindEdgesNodes()
        FindVerticesNodes()
        # Defining Master and Slaves Entities
        MasterDict,EntMastersNames = DictEntities()

        # Searching for Paired Nodes
        def ConcatenateDataframes(olddataframe,dataframe):
            '''
            Method that will concatenate the dataframe given with the olddataframe
            '''
            frames = [olddataframe,dataframe]
            newdataframe = pd.concat(frames)

            return newdataframe

        oldDataFramePaired = None

        print("\n\nSearching for the paired nodes!(it tooks long time)")
        time_paried_nodes_init = perf_counter()


        for i in tqdm(EntMastersNames):
            EntityType = ChooseTypeEntity(i)
            Master_Entity_i_dict = MasterDict[i]
            Slave_Entity_i_dict = TellPairVar(i)
            CoodList = ChooseCoodToReflect(i)

            DataframePairedNodes_i = PariedNodesOfEntities(EntityType,Master_Entity_i_dict,Slave_Entity_i_dict,CoodList,i)
            DataframePairedNodes = ConcatenateDataframes(oldDataFramePaired,DataframePairedNodes_i)

            oldDataFramePaired = DataframePairedNodes

        #print(DataframePairedNodes)
        #input("Press enter")
        #DataframePairedNodes = ReorderDataFrameIndex(DataframePairedNodes)
        time_paried_nodes_end = perf_counter()
        time_elapsed_paried_nodes = time_paried_nodes_end-time_paried_nodes_init
        print("Done! ({})s".format(time_elapsed_paried_nodes))
        self.DataframePairedNodes = DataframePairedNodes
        self.EntMastersNames = EntMastersNames
        self.MasterDict = MasterDict


    def Write_Macro(self,Solve_macroname='macro_to_solve',Solvemacrofolder='Default',StrainStateValue=1,StrainCase='ALL',directory_to_save='Default'):
        '''
        Method to create the Macro will all the commands for solve laterly.
        The process will be simple:
        1) For Each Strain State:
         a) Clear All
         b) Input Geometry
         c) Write CE Commands
         d) Write Commands to save Results

         The user must indicates the path where strain and stress results will be saved. For default,
         it will save in the directory where the files can be found. 
        '''
        import os

        DefaultSeperatorTerminal()
        

        def TellsDirectory():
            '''
            Method to tells the current directory
            '''
            directory = os.getcwd()
            return directory
       
        current_date = TellsDate()
        
        if Solvemacrofolder=='Default':
            Solvemacrofolder=r"{}\Macros".format(TellsCurrentDirectory())
            CheckIfFolderExists(Solvemacrofolder)

        f = open('{}\{}.mac'.format(Solvemacrofolder,Solve_macroname),'w')

        def BeggingCommands(f=f,GeoMacroInput = self.macroname, path = self.geomacro_folder):
            '''
            A method to write the default begging APDL Commands
            '''
            f.write("\n\n\n!****************************************!")
            f.write("\n!----------------------------------------!")
            f.write("\n!Clearing All Data:")
            f.write("\n/CLEAR,START")
            f.write("\n/PREP7")
            f.write("\n/INPUT,'{}','cdb','{}',, 0   ".format(GeoMacroInput,path))
            f.write("\n/SOLU")
            f.write("\nLSCLEAR,ALL")
            f.write("\nCEDELE,ALL")
            f.write("\n!----------------------------------------!")


        def AddExternalDataInFile(File_receptor,File_to_add):
            '''
            Method to add external data from a file, in a 
            '''
            with open (File_to_add,'r') as File_to_add_data:
                data = File_to_add_data.read()
            File_receptor.write(data)

            return None


        def WriteCE(StrainCase):
            '''
            This method will, for each stress case, takes
            the position vector of each entity and write the CE
            commands for paired nodes.
            The process will be simple:
            1) Open a new file for the current Strain Case
            3) For each Entity:
             a) Runs 'PBC_apdl_commands'
             b) Read the tmp file generated
             c) Write the file in current Strain Case 
            4) Save the Giant file
            '''
            f_ce = open('PBC_CE_for_strain_case.tmp','w')
            PairedNodesDataFrame = self.DataframePairedNodes #can be put above
            StrainToapply = StrainState(StrainCase,StrainStateValue)
            f_ce.write("\n!Applying PBC for {} Strain State:".format(StrainCase))
            
            region_counter = 0
            Regions_list = ListRegionNumbers()
            for EachEntity in self.EntMastersNames:
                EntityType = ChooseTypeEntity(EachEntity)
                EntityName = ChooseEntityName(Regions_list[region_counter])
                #print(EntityName)
                #print(Regions_list[region_counter])
                PairedNodes = PairedNodesDataFrame.loc[EntityName]
                #print(PairedNodes)
                #input("Check the dataframe")
                region_counter=region_counter+1
                position_vetor = ChoosePositionVector(EachEntity)
                PBC_apdl_commands(PairedNodes,StrainToapply,position_vetor,EachEntity,EntityType)
                with open ('PBC_CE_Commands.tmp','r') as PBC_commands_file:
                    data = PBC_commands_file.read()
                f_ce.write(data)
                
            f_ce.close()


        def SolveCommands(f=f):
            '''
            Just a method to write the solve Commmands
            '''
            f.write("\n!SOLVING")
            f.write("\nSAVE")
            f.write("\nSOLVE")
            f.write("\nSAVE")


        def CommandsForGivenCase(MainFile,StrainCase):
            '''
            Just a method to write the sequencial commands for a given strain case
            '''
            #Initial Commands:
            BeggingCommands()
            #Write CE Commands for the given case
            WriteCE(StrainCase)
            #Add the CE in main file
            AddExternalDataInFile(File_receptor=MainFile,File_to_add='PBC_CE_for_strain_case.tmp')
            #Write Solve Commands:
            SolveCommands()

            if directory_to_save == 'Default':
                # Save in current directory
                current_directory = TellsDirectory()
                current_directory = r"{}\Results".format(current_directory)
                CheckIfFolderExists(current_directory)
                # Write commands to save results
                apdl_commands_extract_export_results(current_directory,case=StrainCase)
                AddExternalDataInFile(File_receptor=MainFile,File_to_add='commands_for_save.tmp')
            else:
                #Save in directory choosed by user
                # Write commands to save results
                CheckIfFolderExists(directory_to_save) #If the user did not created the folder, it is automatically created
                apdl_commands_extract_export_results(directory_to_save,case=StrainCase)
                AddExternalDataInFile(File_receptor=MainFile,File_to_add='commands_for_save.tmp')

            return None

        f.write("!Macro Created in {}".format(current_date))

        if StrainCase == 'ALL':
            print("Creating Macro for ALL Strain States:")
            StrainStateList = StrainCasesList()
            # Write CE for all cases
            for StrainCase in tqdm(StrainStateList):
                CommandsForGivenCase(MainFile=f,StrainCase=StrainCase)
        else:
            # Write CE for the cases choosed by user:
            print("Creating Macro for {} Strain State(s):".format(StrainCase))
            for StrainChoose in tqdm(StrainCase):
            # Write CE 
                CommandsForGivenCase(MainFile=f,StrainCase=StrainChoose) 


    def ShowStrainCases(self):
        '''
        Just a method to show a list with possible cases to be applied
        '''
        DefaultSeperatorTerminal()
        print("Showing The Possible Strain Case Names (Case Sensity)")
        print("Select one of the list:")
        List = StrainCasesList()
        print(List)
        DefaultSeperatorTerminal()
        return None
     

    def DeleteTempFiles(self):
        '''
        Delete All temp files
        '''
        DeleteTempFiles()
        DefaultSeperatorTerminal()
        print("Temporary files removed!")
        DefaultSeperatorTerminal()
        
        return None