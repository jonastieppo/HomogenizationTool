from typing import TypedDict # for pandas columns annotation

class NodeList(TypedDict):
    n_s : list[int]   # Node number
    x_s : list[float] # x coordinate in global coordinate system
    y_s : list[float] # y coordinate in global coordinate system
    z_s : list[float] # z coordinate in global coordinate system
    u1_s : list[float] | None # Applied displacamente on node for D.O.F 1
    u2_s : list[float] | None # Applied displacamente on node for D.O.F 2
    u3_s : list[float] | None # Applied displacamente on node for D.O.F 3

class Node(TypedDict):
    n : int   # Node number
    x : float # x coordinate in global coordinate system
    y : float # y coordinate in global coordinate system
    z : float # z coordinate in global coordinate system
    u1 : float | None # Applied displacamente on node for D.O.F 1
    u2 : float | None # Applied displacamente on node for D.O.F 2
    u3 : float | None # Applied displacamente on node for D.O.F 3