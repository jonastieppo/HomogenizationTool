'''
Module to apply Uniform Strain (non periodic) boundary conditions in a .cdb arquive
'''
import numpy as np
import pandas as pd
from tqdm import tqdm

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


def CheckIfFolderExists(folder_to_check):
    '''
    Method that will receive a folder path, and check if it exists. If don't, create it
    '''
    import os
    if not os.path.exists(folder_to_check):
        os.makedirs(folder_to_check)

    return os.path.exists(folder_to_check)


def ReadsCDB(filename,filepath):
    '''
    Method that read a cdb file, identifies the nodes, 
    '''

    str_file = "{}\{}.cdb".format(filepath,filename)

    with open(str_file, 'r') as myfile:
        data = myfile.readlines()
        data=np.array(data)

    print("Readind {}.cdb and extracting nodes".format(filename))
    for row in tqdm(range(0,data.shape[0])):
        if data[row]=='(3i9,6e21.13e3)\n':
            nodebegin=row

        if data[row]=='(19i9)\n':
            elementbegin=row

        if data[row]=='       -1\n':
            elementend=row

    #Creating temporary files to be read as dataframes

    print("Creating temporary files to be read as dataframes")
    array=data[nodebegin+1:elementbegin-2]
    f = open("nodecood.temp", "w")
    f.write('        E        I        NA                    B                    C\n')
    for row in range(0,array.shape[0]):
        f.write("{}".format(array[row]))
    f.close()

    # df.iloc[:,1].to_csv('nodecood2.temp',sep=',', header=None)

    print("Creating Nodes coordenates dataframe")

    # df = pd.read_csv('nodecood2.temp',header=None,engine='python',sep=' 0        0')
    df=pd.read_fwf('nodecood.temp', widths=[9,9,9,21,21,21])
    df=df.fillna(0)
    df=df.drop(columns=['I','N'])

    return df


def IdentifyBoundaries(df):
    '''
    Method to identy boundaries in a RVE. Returns a dictionary
    '''
    boundaryEast = max(df['A'])
    boundaryWest = min(df['A'])
    boundaryNorth = max(df['B'])
    boundarySouth = min(df['B'])
    boundaryUpper = max(df['C'])
    boundaryLower = min(df['C'])

    boundaries = {'boundaryEast':boundaryEast,
                  'boundaryWest':boundaryWest,
                  'boundaryNorth':boundaryNorth,
                  'boundarySouth':boundarySouth,
                  'boundaryUpper':boundaryUpper,
                  'boundaryLower':boundaryLower}

    return boundaries  


def CreateNodeComponents(boundaries):
    '''
    This method will create node components for ansys. This node components will be used to apply Boundary
    Conditions
    '''
    print("Writing a file with apdl commands for create components")

    boundaryEast = boundaries['boundaryEast']
    boundaryWest = boundaries['boundaryWest']
    boundaryNorth = boundaries['boundaryNorth']
    boundarySouth = boundaries['boundarySouth']
    boundaryUpper = boundaries['boundaryUpper']
    boundaryLower = boundaries['boundaryLower']

    f = open("BC_components.temp", "w")
    f.write("\n!Creating Nodes Componentes for BC")
    f.write("\n!Selection of nodes by LOC")
    f.write("\nCSYS,0")
    f.write("\nWPCSYS,-1,0")
    f.write("\nALLSELL")
    f.write("\nNSEL,S,LOC,X,{}".format(boundaryEast))
    f.write("\nCM,BoundaryEast,nodes")
    f.write("\nNSEL,S,LOC,X,{}".format(boundaryWest))
    f.write("\nCM,BoundaryWest,nodes")
    f.write("\nNSEL,S,LOC,Y,{}".format(boundaryNorth))
    f.write("\nCM,BoundaryNorth,nodes")
    f.write("\nNSEL,S,LOC,Y,{}".format(boundarySouth))
    f.write("\nCM,BoundarySouth,nodes")
    f.write("\nNSEL,S,LOC,Z,{}".format(boundaryUpper))
    f.write("\nCM,BoundaryUpper,nodes")
    f.write("\nNSEL,S,LOC,Z,{}".format(boundaryLower))
    f.write("\nCM,BoundaryLower,nodes")
    f.close()


def CreateDisplacementFunctions(boundaries,StrainValue):
    '''
    Method to create Functions, on APDL language, to generate displacement fields
    '''
    boundaryEast = boundaries['boundaryEast']
    boundaryWest = boundaries['boundaryWest']
    boundaryNorth = boundaries['boundaryNorth']
    boundarySouth = boundaries['boundarySouth']
    boundaryUpper = boundaries['boundaryUpper']
    boundaryLower = boundaries['boundaryLower']

    print("Writing a file with apdl commands to create Displacemente Field")
    funcname =np.array(['displacement_x','displacement_y','displacement_z'])
    beta = StrainValue

    a1 = abs(boundaryEast - boundaryWest)
    a2 = abs(boundaryNorth - boundarySouth)
    a3 = abs(boundaryUpper - boundaryLower)

    caracteristic_distance = [a1,a3,a3]
    
    limits = np.zeros((3,2))
    limits[0,0] = boundaryEast
    limits[0,1] = boundaryWest
    limits[1,0] = boundaryNorth
    limits[1,1] = boundarySouth
    limits[2,0] = boundaryUpper
    limits[2,1] = boundaryLower

    f = open("functionwriting.temp","w")
    f.write("\n!Displacement Fields Creation")
    f.write("\nFunctionCoodSystem = 0")
    # f.write("\n*SET,beta,{} ".format(beta))
    f.write("\n*DIM,limits,,3,2")
    f.write("  !Centroid in x,y,z, respectively")
    f.write("\n\n!!! BEGIN OF FUNCTION CREATION:\n\n")

    for fielddirection in range(0,3):
        beta_fielddirection = beta*caracteristic_distance[fielddirection]/2
        f.write("\n! Setting the value of beta !")
        f.write("\n*SET,beta,{} ".format(beta_fielddirection))
        f.write("\n!BEGIN OF FUNCTION NAME: {}\n".format(funcname[fielddirection]))
        f.write("\n*SET,FunctionName,'{}' ".format(funcname[fielddirection]))
        f.write("\nlimits({},1)={} ".format(fielddirection+1,limits[fielddirection,0]))
        f.write("\nlimits({},2)={} ".format(fielddirection+1,limits[fielddirection,1]))
        f.write("\n*DIM,%FunctionName%,TABLE,6,13,1,,,,%FunctionCoodSystem%   ")
        f.write("\n!Writing the function in a table. Each number is like click in a keyboard.")
        f.write("\n*SET,%FunctionName%(0,0,1), 0.0, -999")
        f.write("\n*SET,%FunctionName%(2,0,1), 0.0 ")
        f.write("\n*SET,%FunctionName%(3,0,1), %beta%")
        f.write("\n*SET,%FunctionName%(4,0,1), %limits({},{})%".format(fielddirection+1,1))
        f.write("\n*SET,%FunctionName%(5,0,1), %limits({},{})%".format(fielddirection+1,2))
        f.write("\n*SET,%FunctionName%(6,0,1), 0.0 ")
        f.write("\n*SET,%FunctionName%(0,1,1), 1.0, -1, 0, 2, 0, 0, 17")
        f.write("\n*SET,%FunctionName%(0,2,1), 0.0, -2, 0, 1, -1, 3, 17")
        f.write("\n*SET,%FunctionName%(0,3,1),   0, -1, 0, 1, 18, 2, 19")
        f.write("\n*SET,%FunctionName%(0,4,1), 0.0, -3, 0, 1, -2, 4, -1")
        f.write("\n*SET,%FunctionName%(0,5,1), 0.0, -1, 0, 1, -3, 3, {}".format(fielddirection+2))
        f.write("\n*SET,%FunctionName%(0,6,1), 0.0, -2, 0, 2, 0, 0, 17")
        f.write("\n*SET,%FunctionName%(0,7,1), 0.0, -3, 0, 1, -2, 3, 17")
        f.write("\n*SET,%FunctionName%(0,8,1), 0.0, -2, 0, 1, -3, 3, 18")
        f.write("\n*SET,%FunctionName%(0,9,1), 0.0, -3, 0, 1, 18, 2, 19")
        f.write("\n*SET,%FunctionName%(0,10,1), 0.0, -4, 0, 1, -2, 4, -3")
        f.write("\n*SET,%FunctionName%(0,11,1), 0.0, -2, 0, 1, 17, 2, -4")
        f.write("\n*SET,%FunctionName%(0,12,1), 0.0, -3, 0, 1, -1, 1, -2")
        f.write("\n*SET,%FunctionName%(0,13,1), 0.0, 99, 0, 1, -3, 0, 0")
        f.write("\n\n!END OF FUNCTION NAME: {}\n".format(funcname[fielddirection]))
    f.close()

    return None


def ConvertName(StrainCase):
    '''
    Method to Convert the name of Strain Case to that used in past code. Returns a string, with the past value.
    '''

    Old_Names = {'Exx':'UniformStrain_xx',
                 'Eyy':'UniformStrain_yy',
                 'Ezz':'UniformStrain_zz',
                 'Exy':'UniformStrain_xy',
                 'Eyz':'UniformStrain_yz',
                 'Exz':'UniformStrain_xz'
                }

    return Old_Names[StrainCase]


def CreateDisplacementCommands(BC_case,StrainValue,boundaries):
    '''
    This method will receive the desired Strain Cases (BC_case), and write the APDL commands in a file. 
    '''
    print("Writing a file with apdl commands to apply BC")

    CM_names=np.array(['boundaryEast','boundaryWest',
                    'boundaryNorth','boundarySouth',
                    'boundaryUpper','boundaryLower'])

    BC_case = ConvertName(BC_case) #Converting the name to that used here

    beta = StrainValue

    a1 = abs(boundaries['boundaryEast']- boundaries['boundaryWest'])
    a2 = abs(boundaries['boundaryNorth']- boundaries['boundarySouth'])
    a3 = abs(boundaries['boundaryUpper']- boundaries['boundaryLower'])


    beta1 = beta*a1/2
    beta2 = beta*a2/2
    beta3 = beta*a3/2

    funcname =np.array(['%displacement_x%','%displacement_y%','%displacement_z%'])

    D_input_data = {'UniformStrain_xx':[beta1,0,0,-beta1,0,0,
                                        funcname[0],0,0,funcname[0],0,0,
                                    funcname[0],0,0,funcname[0],0,0],
                    'UniformStrain_yy':[0,funcname[1],0,0,funcname[1],0,
                                        0,beta2,0,0,-beta2,0,
                                    0,funcname[1],0,0,funcname[1],0],
                    'UniformStrain_zz':[0,0,funcname[2],0,0,funcname[2],
                                        0,0,funcname[2],0,0,funcname[2],
                                    0,0,beta3,0,0,-beta3],
                    'UniformStrain_xy':[funcname[1],beta1,0,funcname[1],-beta1,0,
                                        beta2,funcname[0],0,-beta2,funcname[0],0,
                                    funcname[1],funcname[0],0,funcname[1],funcname[0],0],
                    'UniformStrain_yz':[0,funcname[2],funcname[1],0,funcname[2],funcname[1],
                                        0,funcname[2],beta2,0,funcname[2],-beta2,
                                    0,beta3,funcname[1],0,-beta3,funcname[1]],
                    'UniformStrain_xz':[funcname[2],0,beta1,funcname[2],0,-beta1,
                                        funcname[2],0,funcname[0],funcname[2],0,funcname[0],
                                        beta3,0,funcname[0],-beta3,0,funcname[0]]}
    D_input= pd.DataFrame(D_input_data)

    #Naming the rows
    str = np.array([])
    for index_name in range(0,CM_names.shape[0]):
        for direction in range(0,3):
            str1="{}_{}".format(CM_names[index_name],direction+1)
            str = np.append(str, str1)
    D_input.index = str

    f = open("BC_creation.temp","w")
    dirr_array = np.array(['X','Y','Z'])

    def BC_case_loc(BC_case):
        '''
        Locates the BC_case in D_input dataframe
        '''
        loc = {'UniformStrain_xx':0,
              'UniformStrain_yy':1,
              'UniformStrain_zz':2,
              'UniformStrain_xy':3,
              'UniformStrain_yz':4,
              'UniformStrain_xz':5}

        return loc[BC_case]

    loc = BC_case_loc(BC_case)

    f.write("\n\n!***************************************!")
    f.write("\n\n!APPLYING THE {} BOUNDARY CONDITION".format(BC_case))
    f.write("\n/SOLU")
    f.write("\nLSCLEAR,ALL")
    for surface in range(0,CM_names.shape[0]):
        f.write("\n\n!Applying boundary condition in component {}".format(CM_names[surface]))
        f.write('\nCMSEL,S,{}'.format(CM_names[surface]))
        for direction in range(0,3):
            f.write("\nD,ALL,U{},{}".format(dirr_array[direction],D_input.iloc[surface*3+direction,loc]))
    f.write("\n")
    f.write("\n!-----------------------------------------!")
    f.write("\n!              SELECTING ALL              !")
    f.write("\n!-----------------------------------------!")
    f.write("\nCMSEL,ALL")
    f.write("\nALLSEL")
    f.write("\n!-----------------------------------------!")
    f.close()


def CreateBC(df,StrainCase,StrainValue):
    '''
    Method that receives a dataframe with nodes, and creates APDL commands for BC.
    '''
    # Identifying the boundaries
    boundaries = IdentifyBoundaries(df)
    # Creating Node Components
    CreateNodeComponents(boundaries)
    # Creating APDL Displament Fields Commands
    CreateDisplacementFunctions(boundaries,StrainValue)
    # Selecting the desired cases
    #BC_cases = SelectStrainCase(StrainCase)
    # Writing Boundary conditions on nodes:
    CreateDisplacementCommands(StrainCase,StrainValue,boundaries)


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


def DeleteTempFiles():
    '''
    A macro to delete the tempory files generated during the execution. 
    '''
    import os
    os.remove('BC_components.temp')
    os.remove('BC_creation.temp')
    os.remove('functionwriting.temp')
    os.remove('nodecood.temp')
    os.remove('commands_for_save.tmp')


    return None


class Non_Periodic_BC():
    '''
    Method to Apply Uniform Strain in a RVE, but only with uniform strain field (doens't need to be periodic)
    geomacroname = Name of the .cdb file (withou extension)
    geomacro_folder = Folder where the .cdb file is. By default, it is in the current folder.  
    '''
    def __init__(self,geomacroname='Default',geomacro_folder='Default'):

        print("Starting the Non Periodic BC Applying:")
        #Reading CDB
        if geomacro_folder == 'Default':
            geomacro_folder = r"{}\CDB Files".format(TellsCurrentDirectory())
            CheckIfFolderExists(geomacro_folder)
            if not CheckIfFolderExists(geomacro_folder):
                print(r"Creating a ..\CDB Files Directory. Put all CDB's there, for best practices. But, the program still works otherway.")
                geomacro_folder = r"{}".format(TellsCurrentDirectory())

        if geomacroname == 'Default':
            geomacroname='geo_macro_created'

        self.nodedataframe = ReadsCDB(geomacroname,geomacro_folder)
        self.geomacroname = geomacroname
        self.geomacro_folder = geomacro_folder


    def Write_Macro(self,Solve_macroname='macro_to_solve',Solvemacrofolder='Default',StrainStateValue=1,StrainCase='ALL',directory_to_save='Default'):
        '''
        This method will create the macro to be solved by Ansys. By default, it writes the macro in ..\Macros Folder,
        with the name 
        '''
        if Solvemacrofolder=='Default':
            Solvemacrofolder=r"{}\Macros".format(TellsCurrentDirectory())
            CheckIfFolderExists(Solvemacrofolder)

        f = open('{}\{}.mac'.format(Solvemacrofolder,Solve_macroname),'w')

        def BeggingCommands(f=f,GeoMacroInput = self.geomacroname, path = self.geomacro_folder):
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
            f.write("\n!----------------------------------------!")


        def AddExternalDataInFile(File_receptor,File_to_add):
            '''
            Method to add external data from a file, in a 
            '''
            with open (File_to_add,'r') as File_to_add_data:
                data = File_to_add_data.read()
            File_receptor.write(data)

            return None


        def CommandsToSolve(f,StrainCase):
            '''
            Method to write in a file f, already open, the commands for saving. 
            '''
            f.write("\n!SOLVING")
            f.write("\nSAVE")
            f.write("\nSOLVE")
            f.write("\nSAVE,'{}','db',".format(StrainCase))

            return None

        def CommandsForEachCase(MainFile,StrainCase):
            
            #Initial Commands:
            BeggingCommands()
            #Creating the macro with Boundary Conditions:
            CreateBC(self.nodedataframe,StrainCase,StrainStateValue)
            #Write Commands to save the results in a external file
            apdl_commands_extract_export_results(directory_to_save,StrainCase)
            #Adding Just Created Files:
            AddExternalDataInFile(MainFile,'BC_components.temp') # Writing Node Components
            AddExternalDataInFile(MainFile,'functionwriting.temp') # Writing Functions
            AddExternalDataInFile(MainFile,'BC_creation.temp') # Applting Boundary Conditions on Node Components
            CommandsToSolve(MainFile,StrainCase) # Writing Commands For Solve the current Case
            AddExternalDataInFile(MainFile,'commands_for_save.tmp') # Adding Commands to export the results


        if StrainCase == 'ALL':
            StrainCase  = ['Exx','Eyy','Ezz','Exy','Eyz','Exz']
        if directory_to_save == 'Default':
            # Save in current directory
            directory_to_save = TellsCurrentDirectory()
            directory_to_save = r"{}\Results".format(directory_to_save)
            CheckIfFolderExists(directory_to_save)

        for Case in StrainCase:
            CommandsForEachCase(MainFile=f,StrainCase=Case)


    def DeleteTempFiles(self):
        '''
        Delete All temp files
        '''
        DeleteTempFiles()
        DefaultSeperatorTerminal()
        print("Temporary files removed!")
        DefaultSeperatorTerminal()
        return None

