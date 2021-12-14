'''
This class will be used to calculate the stiffiness and compliance matrix by CLT. 
The general strategy here is to save all info as dictionary, and when it is necessary,
transforms in array, which itselves can be save in a dataframe. 
'''
import pandas as pd 
import numpy as np 

    
def MatrixEngineeringConstants(E1=3.2E3,v12=0.38):
    '''
    Method to create a default matrix Engineering Constants Information;
    '''
    EngDict = {'E1':E1,
            'v12':v12
            }

    return EngDict

# E1=55.7E3,E2=18.5E3,G12=6.89E3,v12=0.22
# E1=55.7E3,E2=55.7E3,G12=22.82E3,v12=0.22

def Strand_EngineeringConstants(E1=59.3E3,E2=23.2E3,G12=8.68E3,v12=0.21):
    '''
    Method to create a dictionary with Engineering Contants Information of fiber. Default is...
    '''
    EngDict = {'E1':E1,
            'E2':E2,
            'G12':G12,
            'v12':v12,
            }

    return EngDict


def Homogeneous_lamina(Strand_EngineeringConstants=Strand_EngineeringConstants(),Matrix_EngineeringConstants=MatrixEngineeringConstants(),vf=0.65):
    '''
    Given a set of engineering constants, it applies micromechanics and returns a homogenized engineering constants (not for chentsov cof)
    '''
    E1_f = Strand_EngineeringConstants['E1']
    E2_f = Strand_EngineeringConstants['E2'] #Not used, because E1 was calculated with an easy way
    G12_f = Strand_EngineeringConstants['G12']
    v12_f = Strand_EngineeringConstants['v12']

    E1_m = Matrix_EngineeringConstants['E1']
    v12_m = Matrix_EngineeringConstants['v12']

    if vf<1:

        EngineeringConstants = {} #initiating the dictionary
        # Longitudinal Modulus
        EngineeringConstants['E1'] = E1_f*vf+E1_m*(1-vf)
        # Transversal Modulus
        alpha = np.sqrt(vf)
        beta = E1_m/E1_f

        EngineeringConstants['E2'] = E1_m*(1-alpha+alpha/(1-alpha*(1-beta)))

        # Shear Modulus
        G12_m = E1_m/(2*(1+v12_m))
        zeta = 1+40*(vf)**(10)
        eta = (G12_f/G12_m-1)/(G12_f/G12_m+zeta)
        EngineeringConstants['G12'] = G12_m*(1+zeta*eta*vf)/(1-eta*vf)

        # Poisson 
        EngineeringConstants['v12'] = v12_m*(1-vf)+vf*v12_f
    
    if vf == 1:
        EngineeringConstants=Strand_EngineeringConstants

    return EngineeringConstants


def S_anisotropic(EngineeringConstants=Homogeneous_lamina()):
    '''
    Method to create the S_anisotropic. The inputs are the 
    '''
    E1 = EngineeringConstants['E1']
    E2 = EngineeringConstants['E2']
    G12 = EngineeringConstants['G12']
    v12 = EngineeringConstants['v12']

    #Calculating others:
    v21 = E2/E1*v12 

    S_matrix = np.array([[1/E1,-v21/E2, 0],
                        [-v12/E1,1/E2,0],
                        [0, 0,1/G12]])

    return S_matrix


def Q_anisotropic(EngineeringConstants=Homogeneous_lamina()):
    '''
    Creates the Q_anisotropic by inverting the S anisotropic
    '''

    S =  S_anisotropic(EngineeringConstants=EngineeringConstants)

    Q_anisotropic = np.linalg.inv(S)

    return Q_anisotropic


def Tmatrix(angle):
    '''
    Defining the transformation matrix. 'angle' comes in degrees
    '''
    angle = np.radians(angle) #converting to degrees
    cos = np.cos(angle)
    sin = np.sin(angle)

    T = np.array([[cos**2,sin**2,-2*sin*cos],
                [sin**2,cos**2,2*sin*cos],
                [sin*cos,-sin*cos,(cos**2-sin**2)]])
    return T


def Rmatrix():
    '''
    Defining the R matrix (quite don't remember the name)
    '''
    R = np.array([[1,0,0],
                [0,1,0],
                [0,0,2]])
    return R


def Qbar(angle,EngineeringConstants=Homogeneous_lamina()):
    '''
    Defining the Qbar matrix. It receives an angle, and a S (compliance matrix)
    beforehand calculated, or with a default value. 
    '''
    T=Tmatrix(angle)
    R = Rmatrix()
    Rinv = np.linalg.inv(R)
    Tinv = np.linalg.inv(T)

    T_inv_transpose_1 = np.matmul(R,T)
    T_inv_transpose = np.matmul(T_inv_transpose_1,Rinv)
    Q = Q_anisotropic(EngineeringConstants=EngineeringConstants)

    Qbar_1 = np.matmul(Tinv,Q)
    Qbar = np.matmul(Qbar_1,T_inv_transpose)

    return Qbar


def z_info(z1,z2):
    '''
    A dictionary with two values: z1 and z2
    '''
    z_dict = {'z1':z1,
            'z2':z2
            }
    return z_dict


def N_info(Qbar,z_info):
    '''
    A dictionary with two keywords: Qbar and z
    '''

    N_info = {'Qbar':Qbar,
            'z_info':z_info
            }

    return N_info


def A_submatriz(All_N_info):
    '''
    Method to calculate the A submatrix. It receives a dictionary with all information about
    laminae. For example:

    All_N_info = {'n1':N_info1,
                'n2':N_info2,
                'n3':N_info3,
                'n4':N_info4
                    }
    '''
    A_submatriz = np.zeros((3,3))
    for each_laminae in All_N_info:
        Q = All_N_info[each_laminae]['Qbar']
        z_k = All_N_info[each_laminae]['z_info']['z1']
        z_k_next = All_N_info[each_laminae]['z_info']['z2']

        A_submatriz = A_submatriz+Q*(z_k_next-z_k)

    return A_submatriz


def B_submatriz(All_N_info):
    '''
    Method to calculate the A submatrix. It receives a dictionary with all information about
    laminae. For example:

    All_N_info = {'n1':N_info1,
                'n2':N_info2,
                'n3':N_info3,
                'n4':N_info4
                    }
    '''
    B_submatriz = np.zeros((3,3))
    for each_laminae in All_N_info:
        Q = All_N_info[each_laminae]['Qbar']
        z_k = All_N_info[each_laminae]['z_info']['z1']
        z_k_next = All_N_info[each_laminae]['z_info']['z2']

        B_submatriz = B_submatriz+Q*((z_k_next-z_k)*(z_k_next+z_k))

    return B_submatriz*0.5


def D_submatriz(All_N_info):
    '''
    Method to calculate the A submatrix. It receives a dictionary with all information about
    laminae. For example:

    All_N_info = {'n1':N_info1,
                'n2':N_info2,
                'n3':N_info3,
                'n4':N_info4
                    }
    '''
    D_submatriz = np.zeros((3,3))
    for each_laminae in All_N_info:
        Q = All_N_info[each_laminae]['Qbar']
        z_k = All_N_info[each_laminae]['z_info']['z1']
        z_k_next = All_N_info[each_laminae]['z_info']['z2']

        D_submatriz = D_submatriz+1/3*Q*(z_k**3-z_k_next**3)

    return D_submatriz


def MountABD(A_submatriz,B_submatriz,D_submatriz):
    '''
    Method to mount the ABC matrix
    '''
    ABD_1 = np.concatenate((A_submatriz,B_submatriz),1)
    ABD_2 = np.concatenate((B_submatriz,D_submatriz),1)
    ABD = np.concatenate((ABD_1,ABD_2),0)

    return ABD


def CalculateEngineeringConstants(ABD,h):
    '''
    Method to calculate the in-plane engineering constants -
    Eq (84), Eq (85), Eq (86), Eq (88),  Eq (89).
    Returns a dictionary
    '''

    ABD_E11 = ABD[1:6,1:6]

    ABD_E22_P1 = np.array([[ABD[0,0]]])
    ABD_E22_P2 = np.array([ABD[0,2:6]])
    ABD_E22_P3 = ABD_E22_P2.T #T is to transpose, because python interpret as a line, so you have to transpose
    ABD_E22_P4 = np.array(ABD[2:6,2:6])

    ABD_G12_P1 = np.array(ABD[0:2,0:2])
    ABD_G12_P2 = np.array(ABD[0:2,3:6])
    ABD_G12_P3 = ABD_G12_P2.T
    ABD_G12_P4 = np.array(ABD[3:6,3:6])

    p1_e1 = ABD[0,1]
    p1_e2 = ABD[1,2]
    p1_e3 = ABD[2,0]
    p1_e4 = ABD[2,2]

    ABD_vxy_P1_1= np.array([[p1_e1,p1_e2],[p1_e3,p1_e4]])
    ABD_vxy_P2_1 = np.array(ABD[1:3,3:6])
    ABD_vxy_P3_1 = np.array([ABD[0,3:6],ABD[2,3:6]]).T
    ABD_vxy_P4_1 = np.array(ABD[3:6,3:6])
    
    #Mounting the matrix to take the determinant from, to calculate Ey
    ABD_E22_P1_P2 = np.concatenate((ABD_E22_P1,ABD_E22_P2),1)
    ABD_E22_P3_P4 = np.concatenate((ABD_E22_P3,ABD_E22_P4),1)
    ABD_E22 = np.concatenate((ABD_E22_P1_P2,ABD_E22_P3_P4),0)

    #Mounting the matrix to take the determinant from,to calculate Gxy
    ABD_G12_P1_P2 = np.concatenate((ABD_G12_P1,ABD_G12_P2),1)
    ABD_G12_P3_P4 = np.concatenate((ABD_G12_P3,ABD_G12_P4),1)
    ABD_G12 = np.concatenate((ABD_G12_P1_P2,ABD_G12_P3_P4),0)
    
    #Mounting the matrix to take the determinant from, to calculate vxy
    ABD_vxy_P1_1_P2_1 = np.concatenate((ABD_vxy_P1_1,ABD_vxy_P2_1),1)
    ABD_vxy_P3_1_P4_1 = np.concatenate((ABD_vxy_P3_1,ABD_vxy_P4_1),1)
    ABD_vxy_1 = np.concatenate((ABD_vxy_P1_1_P2_1,ABD_vxy_P3_1_P4_1),0)

    Ex = np.linalg.det(ABD)/(np.linalg.det(ABD_E11))*(1/h)
    Ey = np.linalg.det(ABD)/(np.linalg.det(ABD_E22))*(1/h)
    Gxy = np.linalg.det(ABD)/(np.linalg.det(ABD_G12))*(1/h)
    vxy = np.linalg.det(ABD_vxy_1)/(np.linalg.det(ABD_E11))

    return Ex,Ey,Gxy,vxy


#Building an example (Nasa document)

# Eng_dict = EngineeringConstants(E1=54.87,E2=18.32,G12=8.9,v12=0.25)
#Eng_dict = EngineeringConstants()

# Qbar_0 = Qbar(0)
# Qbar_90 = Qbar(90)
# Qbar_angle = Qbar(45)


# z_info1 = z_info(-0.09,0)
# z_info2 = z_info(0,0.09)

# Ninfo1 = N_info(Qbar_0,z_info1)
# Ninfo2 = N_info(Qbar_90,z_info2)
# Laminate_info = {
#                  'n1':Ninfo1,
#                  'n2':Ninfo2
#                 }


# A = A_submatriz(Laminate_info)
# B = B_submatriz(Laminate_info)
# D = D_submatriz(Laminate_info)

# ABD = MountABD(A,B,D)

# teste = 10
# Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,0.18)


def CalculateComp(material,h,angles):
    '''
    Method to calculate the composite, given an thickness and number of laminas, and, of course,
    the constituints.
    material is a dictionary
    N a integer
    angles is a list
    h is a float
    '''
    N = len(angles)

    # Calculating the Qbars for each angle
    Q_angled = []
    for angle_i in angles:
        Q_angled.append(Qbar(angle_i,material))
    #Calculating the z'
    z_0 = -h/2
    z_list = []
    laminate_info = {}
    for i in range(0,N):
        z1_i = z_0+h/N*i
        z2_i = z1_i+h/N
        z = z_info(z1_i,z2_i)
        lamina_info = N_info(Q_angled[i],z)
        lamina_info_dict = {f'N{i}':lamina_info}
        laminate_info.update(lamina_info_dict)

    # Calculating A,B,D
    A = A_submatriz(laminate_info)
    B = B_submatriz(laminate_info)
    D = D_submatriz(laminate_info)

    ABD = MountABD(A,B,D)

    #Calculating Engineering Constants
    Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,h)

    Results_Eng = {'E1':Ex,
                   'E2':Ey,
                   'G12':Gxy,
                   'v12':vxy
                    }

    return Results_Eng
    

def Calculate_N_ply_Comp(material,h,Diffangles):
    '''
    Method to calculate the engineering Constants, given the number of plyes
    and the difference of angles between laminas. 
    '''
    def ChooseAngles(DefaseAngle):
        '''
        Method to return the angles of the composite, dephased by some input
        '''
        angles = [0+DefaseAngle,90+DefaseAngle,90+DefaseAngle,0+DefaseAngle]
        return angles
    
    N = 4*len(Diffangles)
    h_total = h*len(Diffangles) 

    Q_angled = []
    for deph_angle in Diffangles:
        # Calculating the Qbars for each angle
        angles = ChooseAngles(deph_angle)
        for angle_i in angles:
            Q_angled.append(Qbar(angle_i,material))
    #Calculating the z'
    z_0 = -h_total/2
    laminate_info = {}
    for i in range(0,N):
        z1_i = z_0+h_total/N*i
        z2_i = z1_i+h_total/N
        z = z_info(z1_i,z2_i)
        lamina_info = N_info(Q_angled[i],z)
        lamina_info_dict = {f'N{i}':lamina_info}
        laminate_info.update(lamina_info_dict)

    # Calculating A,B,D
    A = A_submatriz(laminate_info)
    B = B_submatriz(laminate_info)
    D = D_submatriz(laminate_info)

    ABD = MountABD(A,B,D)

    #Calculating Engineering Constants
    Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,h_total)

    Results_Eng = {'E1':Ex,
                   'E2':Ey,
                   'G12':Gxy,
                   'v12':vxy
                    }

    return Results_Eng
   
def PlainWeave_experimental_CLT():
    '''
    Method to analyse the E-glass/Epoxy Plain Weave
    '''
    E_glass_vinylester_80 = {'E1':57.5E3,
                    'E2':18.8E3,
                    'G12':7.44E3,
                    'G23':2.26E3,
                    'v12':0.25,
                    'v23':0.29,
                    'vf':0.6875,
                    'Name':r'E-glass/VinylEster 80%'
                        }

    Vinylester = {'E1':3.4E3,
            'v12':0.35,
            'Name':r'Vinylester'
            }

    homogenized_lamina = Homogeneous_lamina(E_glass_vinylester_80,Vinylester,vf=E_glass_vinylester_80['vf'])
    Qbar_0 = Qbar(0,EngineeringConstants=homogenized_lamina)
    Qbar_90 = Qbar(90,EngineeringConstants=homogenized_lamina)
    z_info1 = z_info(-0.05,0)
    z_info2 = z_info(0,0.05)
    Ninfo1 = N_info(Qbar_0,z_info1)
    Ninfo2 = N_info(Qbar_90,z_info2)
    Laminate_info = {
                    'n1':Ninfo1,
                    'n2':Ninfo2
                    }
    A = A_submatriz(Laminate_info)
    B = B_submatriz(Laminate_info)
    D = D_submatriz(Laminate_info)

    ABD = MountABD(A,B,D)

    h=0.1
    Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,h)

    Results_Eng = {'E1':Ex,
                   'E2':Ey,
                   'G12':Gxy,
                   'v12':vxy
                    }

    return Results_Eng

def PlainWeave_experimental_CLT_2():
    '''
    Method to analyse the E-glass/Epoxy Plain Weave
    '''
    E_glass_vinylester_80 = {'E1':57.5E3,
                    'E2':18.8E3,
                    'G12':7.44E3,
                    'G23':2.26E3,
                    'v12':0.25,
                    'v23':0.29,
                    'vf':0.6875,
                    'Name':r'E-glass/VinylEster 80%'
                        }

    Vinylester = {'E1':3.4E3,
            'v12':0.35,
            'Name':r'Vinylester'
            }

    homogenized_lamina = Homogeneous_lamina(E_glass_vinylester_80,Vinylester,vf=E_glass_vinylester_80['vf'])
    Qbar_0 = Qbar(0,EngineeringConstants=homogenized_lamina)
    Qbar_90 = Qbar(90,EngineeringConstants=homogenized_lamina)
    z_info1 = z_info(-0.05,-0.025)
    z_info2 = z_info(-0.025,0)
    z_info3 = z_info(0,0.025)
    z_info4 = z_info(0.025,0.05)
    Ninfo1 = N_info(Qbar_0,z_info1)
    Ninfo2 = N_info(Qbar_90,z_info2)
    Ninfo3 = N_info(Qbar_90,z_info3)
    Ninfo4 = N_info(Qbar_0,z_info4)

    Laminate_info = {
                    'n1':Ninfo1,
                    'n2':Ninfo2,
                    'n3':Ninfo3,
                    'n4':Ninfo4,
                    }
    A = A_submatriz(Laminate_info)
    B = B_submatriz(Laminate_info)
    D = D_submatriz(Laminate_info)

    ABD = MountABD(A,B,D)
    h=0.1
    Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,h)

    Results_Eng = {'E1':Ex,
                   'E2':Ey,
                   'G12':Gxy,
                   'v12':vxy
                    }

    return Results_Eng

def Eight_harness_experimental_CLT():

    '''
    Method to analyse the E-glass/Epoxy Plain Weave
    '''
    E_glass_epoxy_80 = {'E1':59.3E3,
                    'E2':23.2E3,
                    'G12':8.68E3,
                    'G23':7.60E3,
                    'v12':0.21,
                    'v23':0.32,
                    'vf':0.65,
                    'Name':r'E-glass/Epoxy 80%'
                        }

    Epoxy = {'E1':3.2E3,
            'v12':0.38,
            'Name':r'Epoxy'
            }

    homogenized_lamina = Homogeneous_lamina(E_glass_epoxy_80,Epoxy,vf=E_glass_epoxy_80['vf'])
    Qbar_0 = Qbar(0,EngineeringConstants=homogenized_lamina)
    Qbar_90 = Qbar(90,EngineeringConstants=homogenized_lamina)
    z_info1 = z_info(-0.09,0)
    z_info2 = z_info(0,0.09)
    Ninfo1 = N_info(Qbar_0,z_info1)
    Ninfo2 = N_info(Qbar_90,z_info2)
    Laminate_info = {
                    'n1':Ninfo1,
                    'n2':Ninfo2
                    }
    A = A_submatriz(Laminate_info)
    B = B_submatriz(Laminate_info)
    D = D_submatriz(Laminate_info)

    ABD = MountABD(A,B,D)

    h=0.18
    Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,h)

    Results_Eng = {'E1':Ex,
                   'E2':Ey,
                   'G12':Gxy,
                   'v12':vxy
                    }

    return Results_Eng

def two_two_twill_weave_CLT():
    '''
    Method to analyse the E-glass/Epoxy Plain Weave
    '''
    E_glass_epoxy_75 = {'E1':55.7E3,
                    'E2':18.5E3,
                    'G12':6.89E3,
                    'G23':6.04E3,
                    'v12':0.22,
                    'v23':0.34,
                    'vf':0.50666,
                    'Name':r'E-glass/Epoxy 75'
                        }

    Epoxy = {'E1':3.2E3,
            'v12':0.38,
            'Name':r'Epoxy'
            }

    homogenized_lamina = Homogeneous_lamina(E_glass_epoxy_75,Epoxy,vf=E_glass_epoxy_75['vf'])
    Qbar_0 = Qbar(0,EngineeringConstants=homogenized_lamina)
    Qbar_90 = Qbar(90,EngineeringConstants=homogenized_lamina)
    z_info1 = z_info(-0.1135,0)
    z_info2 = z_info(0,0.1135)
    Ninfo1 = N_info(Qbar_0,z_info1)
    Ninfo2 = N_info(Qbar_90,z_info2)
    Laminate_info = {
                    'n1':Ninfo1,
                    'n2':Ninfo2
                    }
    A = A_submatriz(Laminate_info)
    B = B_submatriz(Laminate_info)
    D = D_submatriz(Laminate_info)

    ABD = MountABD(A,B,D)

    h=0.2275
    Ex,Ey,Gxy,vxy = CalculateEngineeringConstants(ABD,h)

    Results_Eng = {'E1':Ex,
                    'E2':Ey,
                    'G12':Gxy,
                    'v12':vxy
                    }

    return Results_Eng

def ExperimentalResults():
    '''
    Method just to show the experimental results, 
    in a dictionary fashion
    '''
    PlainWeave = {

        'E1':24.8E3,
        'E2':24.8E3,
        'G12':6.5E3,
        'v12':0.1,
    }

    EightHarness = {

        'E1':25.6E3,
        'E2':26.03E3,
        'G12':5.7E3,
        'v12':0.13,

    }

    TwillWeave = {

        'E1':19.2E3,
        'E2':19.54E3,
        'G12':3.6E3,
        'v12':0.13,

    }

    ScidaResults = {

        'E-glass/vinylester plain-weave':PlainWeave,
        'E-glass eight-harness satin weave/epoxy':EightHarness,
        '2/2 twill E-glass woven fabric/epoxy':TwillWeave
    }

    return ScidaResults