from typing import TypedDict # for pandas columns annotation

class NodeList(TypedDict):
    n : list[int]   # Node number
    x : list[float] # x coordinate in global coordinate system
    y : list[float] # y coordinate in global coordinate system
    z : list[float] # z coordinate in global coordinate system
    u1 : list[float] | None # Applied displacamente on node for D.O.F 1
    u2 : list[float] | None # Applied displacamente on node for D.O.F 2
    u3 : list[float] | None # Applied displacamente on node for D.O.F 3

class Node(TypedDict):
    n : int   # Node number
    x : float # x coordinate in global coordinate system
    y : float # y coordinate in global coordinate system
    z : float # z coordinate in global coordinate system
    u1 : float | None # Applied displacamente on node for D.O.F 1
    u2 : float | None # Applied displacamente on node for D.O.F 2
    u3 : float | None # Applied displacamente on node for D.O.F 3