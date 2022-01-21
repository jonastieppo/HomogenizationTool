import pandas as pd
import numpy as np
from tqdm import tqdm

def Open_TexGen_inp(FileFolder,File):
    '''
    Method that will open an File.inp arquive,
    located in FileFolder. As usual, FileFolder and File are 
    strings.
    
    Returns an array, where each position is a arquive line.
    '''
    with open(r'{}\{}.inp'.format(FileFolder,File), 'r') as myfile:
        data = myfile.readlines()
        DataArray=np.array(data)
    
    return DataArray


def Tell_Element_Type_Name_Abaqus(Type):
    '''
    Will returnts the Element type name used by Abaqus
    '''
    
    if Type == 'Quadratic':
        return 'C3D10'
    if Type == 'Linear':
        return 'C3D4'
    
    return 'Error: Use "Quadratic" or "Linar"'


def Tell_Element_Type_Name_Ansys(Type):
    '''
    Will returnts the Element type name used by Abaqus
    '''
    
    if Type == 'Quadratic':
        return 'SOLID187'
    if Type == 'Linear':
        return 'SOLID185'
    
    return 'Error: Use "Quadratic" or "Linar"'


def Get_Node_Element_Data_position(DataArray,ElementType):
    '''
    This method identifies where the node data and element data are located in 
    .inp file from TexGen.
    
    It returns a Dictionary
    '''
    ElementName = Tell_Element_Type_Name_Abaqus(ElementType)
    flag = 0
    for row in tqdm(range(0,DataArray.shape[0])):
        if DataArray[row] == '*Node\n' and flag==0:
            NodeLineBegin=row #A contagem das linhas é em zero, então vai parecer errado
            flag=1
        if DataArray[row] == '*Element, Type={}\n'.format(ElementName):
            NodeLineEnd=row
        if (DataArray[row] == '********************\n' and 
            DataArray[row+1] == '*** ORIENTATIONS ***\n'):
            ElementLineEnd=row
            
    NodeElementDataLoc = {'NodeLineBegin':NodeLineBegin,
                          'NodeLineEnd':NodeLineEnd,
                          'ElementLineEnd':ElementLineEnd,
                         }

    return NodeElementDataLoc


def Macro_Setup(ElementType):
    '''
    This method creates the first lines by Ansys, in the step where the geometry
    is begin generated. 
    '''
    from datetime import date
    today = date.today()
    AnsysElementName = Tell_Element_Type_Name_Ansys(ElementType)
    
    f = open("macrosetup.temp","w")
    f.write("\n!MACRO TRANSLATED FROM TEXGEN BY JONAS ({})".format(today.strftime("%d/%m/%Y")))
    f.write("\n!Preprocessing apdl commands")
    f.write("\n/PREP7")
    f.write("\nET,1,{}".format(AnsysElementName))
    f.write("\nSHPP,OFF")
    f.write("\n/NOPR")
    f.write("\nSAVE")
    f.close()
    
    return None


def Node_Temp_File(DataArray,NodeElementDataLoc):
    '''
    Method that receives an array with all Element and Node Data,
    and creates a temporary node file to 
    be read as dataframe
    '''
    NodeLineBegin = NodeElementDataLoc['NodeLineBegin']
    NodeLineEnd = NodeElementDataLoc['NodeLineEnd']
    array=DataArray[NodeLineBegin:NodeLineEnd]
    
    print("Creating nodecood.temp temporary file:")
    f = open("nodecood.temp", "w")
    for row in tqdm(range(0,array.shape[0])):
        f.write("{}".format(array[row]))
    f.close()
    
    return None


def Element_Temp_File(DataArray,NodeElementDataLoc):
    '''
    Method that receives an array with all Element and Node Data,
    and creates a temporary element file 
    be read as dataframe
    '''
    NodeLineEnd = NodeElementDataLoc['NodeLineEnd']
    ElementLineEnd = NodeElementDataLoc['ElementLineEnd']
    array=DataArray[NodeLineEnd:ElementLineEnd]
    
    print("Creating elementconnect.temp temporary file:")
    f = open("elementconnect.temp", "w")
    for row in tqdm(range(0,array.shape[0])):
        f.write("{}".format(array[row]))
    f.close()
    
    return None   
    

def Create_Node_DataFrame():
    '''
    Read the temporary file created, and creates a dataframe. It exports
    and dataframe that is identical to ansys commands
    '''
    df = pd.read_csv('nodecood.temp', sep = ',',skiprows=1, header=None)
    df.insert(0, "!Node Command", "N")
    df.to_csv('nodecood.temp', sep=',', index=False)#Saving a external file
    
    return None


def Create_Element_DataFrame(ElementType):
    '''
    Read the temporary file created, and creates a dataframe
    '''
    df = pd.read_csv('elementconnect.temp', sep = ',',skiprows=1, header=None)

    if ElementType=='Quadratic':
        
        df_Emore = pd.DataFrame(data = df.drop(columns=[0,1,2,3,4,5,6,7,8])) #Creating a second dataframe with the extra nodes

        df=df.drop(columns=[0,9,10]) #Dropping of the element numeration (because it is not used in ANSYS) and the last two columns that will be declared in EMORE command
        df.insert(0, "!E Command", "E")
        df_Emore.insert(0,"!EMORE Command","EMORE")

        df.to_csv('Ecommands.temp', sep=',', index=False)#Saving a external file
        df_Emore.to_csv('Emorecommands.temp',sep =',', index = False)

        with open(r'Ecommands.temp', 'r') as myfile:
            dataE = myfile.readlines()
            dataE=np.array(dataE)
        with open(r'Emorecommands.temp', 'r') as myfile:
            dataEmore = myfile.readlines()
            dataEmore = np.array(dataEmore)

        print("Writing Temporary element file Commands")
        f = open('elementconnect.temp','w')
        for i in tqdm(range(df.shape[0]+1)): #I have no clue, but I have to force print one more value
            f.write(r"{}".format(dataE[i]))
            f.write(r"{}".format(dataEmore[i]))
        f.close()
        
        import os 
        os.remove('Ecommands.temp')
        os.remove('Emorecommands.temp')
        
    if ElementType=='Linear':

        df=df.drop(columns=0) #Dropping of the element numeration (because it is not used in ANSYS)
        df.insert(0, "!Element Command", "E")
        #print("This is the the new element connectivity dataframe: \n{}".format(df))
        df.to_csv('elementconnect.temp', sep=',', index=False)#Saving a external file
    
    return None


def Open_TexGen_ori(FileFolder,File):
    '''
    Method to read an TexGen .ori file. 
    
    Returns a dataframe
    '''
    print("Reading {}.ori...".format(File))
    df = pd.read_csv('{}\{}.ori'.format(FileFolder,File),skiprows=7,header=None)
    
    return df


def Write_Local_Cood_APDL_temp_file(df):
    '''
    Method that will receive a dataframe, and calculates the local angles of
    each element. A temporary file, with APDL Commands is generated
    '''
    print("Creating Local Coordinates")

    arr = np.array

    x_rot = np.zeros((df.shape[0],1))
    z_rot = np.zeros((df.shape[0],1))
    
    print("Calculating rotatation angles")
    for row in tqdm(range(0,df.shape[0])):
        x_rot[row] = arr(np.rad2deg(np.arccos(df.iloc[row,1])))
        #df.iloc[row,5] =  np.absolute(df.iloc[row,5])
        e1 = arr([df.iloc[row,1],df.iloc[row,2],df.iloc[row,3]])
        e2 = arr([df.iloc[row,4],np.absolute(df.iloc[row,5]),df.iloc[row,6]])
        z_rot[row] = arr(np.rad2deg(np.arccos((np.cross(e1,e2)[2]))))
    # #The last line is a bit tricky. It takes the cross-product between the
    # # vector e1 and e2(forced to respect the right hand rule), and pull off 
    # #from it the arccos of the dot product between the 3rd vector and z-axys,
    # # which would result in just the k component (see anton pg.806).
    
    print("Creating data for dataframe:")
    df.loc[:,0]=df.loc[:,0]+10
    ang3 = np.zeros((df.shape[0],1))
    data = {'CS':df[0],'xgr':x_rot[:,0],'zlr':z_rot[:,0],'ang3':ang3[:,0]}
    
    print("Assigning rotation angles to a dataframe:")
    df_localcood = pd.DataFrame(data=data)
    
    print("Creating localcood.temp temporary arquive..")
    f = open("localcood.temp", "w")
    f.write("\n!Creating Local Cood Sys")
    f.write("\n*dim,local_cood,array,{},4".format(df_localcood.shape[0]))
    f.write("  !Local Coordinates Array")
    for row in tqdm(range(0,df_localcood.shape[0])):
        f.write("\nlocal_cood({},1)={}".format(row+1,df_localcood.iloc[row,0])) #KCN
        f.write("\nlocal_cood({},2)={}".format(row+1,df_localcood.iloc[row,1])) #Ang1
        f.write("\nlocal_cood({},3)={}".format(row+1,df_localcood.iloc[row,2])) #Ang2
        f.write("\nlocal_cood({},4)={}".format(row+1,df_localcood.iloc[row,3])) #Ang3
        
    # #Aqui, apesar do elemento fazer apenas uma rotação, eu tenho que criar um sistema de coordenadas intermediário. Esse sistema
    # # intermediário consiste numa rotação em torno do Z global, de (0-90) graus ou qualquer ângulo de fabricação do compósito. 
    # # Então, alinha-se o sistema de coordenadas com este último local criado, e se faz uma rotação em torno do x local, indicando 
    # # a curvatura da fibra.
    
    f.write("\n!Assigning Local Coordinate System")
    f.write("\n\n*DO,i,1,{},1".format(df_localcood.shape[0]))
    f.write("\nCSYS,0") #Colocando com referencial o sistema global
    f.write("\nCLOCAL, local_cood(i,1), 0, 0, 0, 0, local_cood(i,2), , ,") #Primeira rotação
    f.write("\nCSYS,local_cood(i,1)") #Colocando com referencial o sistema local temperário
    f.write("\nCLOCAL, local_cood(i,1), 0, 0, 0, 0, 0, 0,local_cood(i,3)") #Segunda rotação, em torno do sistema local
    f.write("\nEMODIF, i, ESYS, local_cood(i,1)") #Colocando o sistema criado como referencial
    f.write("\n*ENDDO")
    f.write("\nSAVE")  
    f.close()

    f.close()
    
    return None
    

def Open_TexGen_eld(FileFolder,File):
    '''
    Opens the .eld file from texgen. 
    
    Returns a dataframe
    '''
    
    print("Reading {}.eld ".format(File))
    df = pd.read_csv('{}\{}.eld'.format(FileFolder,File),skiprows=8,header=None)
    
    return df


def Identify_Matrix_and_Fiber(df):
    '''
    Identifies matrix and fibers elements. It will creates a temporary file
    with element information: whether it its matrix or fiber. Further, once they are 
    identified, node componenents are generated.
    '''
    df = df.sort_values(by=1)
    
    row=0
    while(df.iloc[row,1]==-1):
        last_matrix_element = df.iloc[row,0]
        row=row+1

    # Discovering how many elements are identified as matrix

    matrix_elements = np.zeros((row,1))
    fiber_elements = np.zeros((df.shape[0]-row,1))

    for matrixrow in tqdm(range(0,row)):
        matrix_elements[matrixrow]=df.iloc[matrixrow,0]

    for fiberrow in tqdm(range(1,df.shape[0]-row)):
        fiber_elements[fiberrow]=df.iloc[fiberrow+row-1,0]

    df = pd.DataFrame(data={'Element Number':matrix_elements[:,0]})
    df.insert(1, "Material", 1)

    df2 = pd.DataFrame(data={'Element Number':fiber_elements[:,0]})
    df2.insert(1, "Material", 2)

    df=df.append(df2)

    #writing a file for apdl commands

    print("Creating matinfo.temp temporary file")
    f = open("matinfo.temp", "w")
    f.write("!Creating material info")
    f.close()

    #print(df.shape[0])
    f = open("matinfo.temp", "a")
    f.write("\n*dim,mat_info,array,{},2".format(df.shape[0]))
    for row in tqdm(range(0,df.shape[0])):
        f.write("\nmat_info({},1)={}".format(row+1,df.iloc[row,0]))
        f.write("\nmat_info({},2)={}".format(row+1,df.iloc[row,1]))

    f.write("\n!Assigin Properties")    
    f.write("\n*DO,i,1,{},1".format(df.shape[0]))
    f.write("\nEMODIF, mat_info(i,1), MAT, mat_info(i,2)")
    f.write("\n*ENDDO")

    f.write("\n!Creating Elements Components")    
    f.write("\nESEL,S, , ,{}".format(matrix_elements[0,0])) #selecionando o primeiro elemento na lista
    print("Writing APDL commands for select Matrix Elements")
    for row in tqdm(range(1,matrix_elements.shape[0])):
        f.write("\nESEL,A, , ,{}".format(matrix_elements[row,0]))

    f.write("\n!Creating Components for matrix")
    f.write("\nCM,matrix,ELEM")


    f.write("\nESEL,S, , ,{}".format(fiber_elements[1,0])) #selecionando o primeiro elemento na lista
    print("Writing APDL commands for select Fibers Elements")
    #print(fiber_elements[1,0])
    #input("Press Enter to continue...")
    for row in tqdm(range(1,fiber_elements.shape[0])):
        f.write("\nESEL,A, , ,{}".format(fiber_elements[row,0]))

    f.write("\n!Creating Components for Fibers")
    f.write("\nCM,fibers,ELEM")

    f.close()
    
    return None   


def Tow_Properties(Property,Value):
    '''
    Method that receives a Property Name (keyword) and
    a value, associated to it. It retunrs a dataframe
    '''
    FiberProperties = {
                       'Name':None,
                       'E1':None,
                       'E2':None,
                       'v12':None,
                       'v23':None,
                       'G23':None,
                       'G12':None,
                       'vf':None
                      }
    
    return FiberProperties


def Matrix_Properties(Property,Value):
    '''
    Method that receives a Property Name (keyword) and
    a value, associated to it. It retunrs a dataframe
    '''
    Matrix_Properties = {
                       'Name':None,
                       'E1':None,
                       'v12':None,
                      }
    
    return Matrix_Properties


def Write_APDL_mat_commands(Tow_Properties,Matrix_Properties):
    '''
    This method writes APDL commands to assign material data. 
    It receives as input two dictionaries: Tow_Properties and Matrix_Properties.
    '''
    print("Writing APDL Commands for Material Assignment:")
    #Isotropic Material (for matrix):
    EX_m = Matrix_Properties['E1']
    PRXY_m = Matrix_Properties['v12']
    matrix_name = Matrix_Properties['Name']

    #Writing APDL Commands:
    f = open('ansysmatinput.temp','w')
    f.write('!Material Input')
    #f.write('\n/PREP7')
    f.write('\n!Matrix {} Mat Properties'.format(matrix_name))
    f.write('\nMPTEMP,,,,,,,,  ')
    f.write('\nMPTEMP,1,0  ')
    f.write('\nMPDATA,EX,1,,{}'.format(EX_m))
    f.write('\nMPDATA,PRXY,1,,{}'.format(PRXY_m))

    #Transversaly Isotropic Material Relations (for fiber) - Ansys Theory Reference:
    EX =  Tow_Properties['E1']
    EY = Tow_Properties['E2']
    PRXY = Tow_Properties['v12']
    PRYZ = Tow_Properties['v23']
    GXY = Tow_Properties['G12']
    EZ =  EY
    #PRXZ = PRYZ*EX/EY
    PRXZ = PRYZ
    #GYZ = EY/(2*(1+PRXZ))
    GYZ = Tow_Properties['G23']
    GXZ = GYZ
    vf = Tow_Properties['vf']
    fiber_name =  Tow_Properties['Name']
    
    #If vf<1, apply micromechanics
    if vf<1:
        EX = vf*EX+(1-vf)*EX_m 
        alpha=np.sqrt(vf)/(1-np.sqrt(vf)*(1-EX_m/EX))
        EY = EX_m*((1-np.sqrt(vf))+alpha)
        EZ = EY
        PRXY = (1-vf)*PRXY_m+vf*PRXY

        G_m = EX_m/(2+(1+PRXY_m))

        psi = 1+40*(vf)**(10)
        eta_xy = (GXY/G_m-1)/(GXY/G_m+psi)

        GXY = G_m*(1+psi*eta_xy*vf)/(1-eta_xy*vf)

        psi = 1+40*(vf)**(10)
        eta_yz = (GYZ/G_m-1)/(GYZ/G_m+psi)

        GYZ = G_m*(1+psi*eta_yz*vf)/(1-eta_yz*vf)
        GXZ = GYZ
        
    f.write('\n!Fiber {} Mat Properties'.format(fiber_name))
    f.write('\nMPTEMP,,,,,,,,  ')
    f.write('\nMPTEMP,1,0  ')
    f.write('\nMPDATA,EX,2,,{}'.format(EX))
    f.write('\nMPDATA,EY,2,,{}'.format(EY))
    f.write('\nMPDATA,EZ,2,,{}'.format(EZ))
    f.write('\nMPDATA,PRXY,2,,{}'.format(PRXY))
    f.write('\nMPDATA,PRYZ,2,,{}'.format(PRYZ))
    f.write('\nMPDATA,PRXZ,2,,{}'.format(PRXZ))
    f.write('\nMPDATA,GXY,2,,{}'.format(GXY))
    f.write('\nMPDATA,GYZ,2,,{}'.format(GYZ))
    f.write('\nMPDATA,GXZ,2,,{}'.format(GXZ))

    f.close()
    

def TellsCurrentDirectory():
    '''
    A method to tell the current directory
    '''
    import os
    directory = os.getcwd()
    return directory


def DeleteTempFile():
    '''
    Delete Temporary Generated arquives
    '''
    import os
    os.remove("macrosetup.temp")
    os.remove("ansysmatinput.temp")
    os.remove("nodecood.temp")
    os.remove("elementconnect.temp")
    os.remove("localcood.temp")
    os.remove("matinfo.temp")

    print("Temporary files removed!")

    return None


def DefaultComposite():

    #Data from Scida[1999]

    Tow_Properties = {}
    Matrix_Properties = {}

    Tow_Properties['E1'] = 59.3E3
    Tow_Properties['E2'] = 23.2E3
    Tow_Properties['v12'] = 0.21
    Tow_Properties['v23'] = 0.32
    Tow_Properties['G12'] = 8.68E3
    Tow_Properties['G23'] = 7.60E3
    Tow_Properties['vf'] = 1
    Tow_Properties['Name'] = r"E_glass/Epoxy"

    Matrix_Properties['E1'] = 3.2
    Matrix_Properties['v12'] = 0.38
    Matrix_Properties['Name'] = r"Epoxy"

    return Tow_Properties,Matrix_Properties


def SaveCDB(cdb_name,folder):
    '''
    Method that generates a string with the APDL commands to save de cdb.
    '''
    file = r'{}'.format(cdb_name)
    command = "CDWRITE,DB,'{}\{}','cdb',,'',''".format(folder,file)

    return command


def CheckIfFolderExists(folder_to_check):
    '''
    Method that will receive a folder path, and check if it exists. If don't, create it
    '''
    import os
    if not os.path.exists(folder_to_check):
        os.makedirs(folder_to_check)

    return None

class TexGen_Mesh_to_cdb():
    '''
    This will translate an TexGen mesh to an ansys cdb.
    '''
    
    def __init__(self):
        
        print("Starting the Texgen Mesh Translator:")
        #print an explanation of possible functios
        return None


    def AssingnMaterial(self,Tow_Properties='Default',Matrix_Properties='Default'):
        '''
        Assign material properties for tows and matrix
        '''
        if (Tow_Properties=='Default')*(Matrix_Properties=='Default'):
            Tow_Properties,Matrix_Properties=DefaultComposite()

        Write_APDL_mat_commands(Tow_Properties,Matrix_Properties)

        return None


    def TranslateTexGenFiles(self,ElementType='Quadratic',FileFolder='Default',File='Default'):
        '''
        Translate the Output Arquives from Texgen
        '''
        if FileFolder=='Default':
            FileFolder = TellsCurrentDirectory()
        
        if File == 'Default':
            File = 'mesh'

        # Write Macro Setup Temporary File:
        Macro_Setup(ElementType)
        # Opening .inp file:
        DataArray = Open_TexGen_inp(FileFolder,File)
        # Identifying Node and Element Data:
        NodeElementDataLoc = Get_Node_Element_Data_position(DataArray,ElementType)
        # Creating Node Temporary File:
        Node_Temp_File(DataArray,NodeElementDataLoc)
        # Creating Element Temporary File:
        Element_Temp_File(DataArray,NodeElementDataLoc)
        # Creating a dataframe identical to ansys commands for nodes
        Create_Node_DataFrame()
        # Creating a dataframe identical to ansys commands for Element
        Create_Element_DataFrame(ElementType)
        # Opening TexGen .ori arquive:
        df = Open_TexGen_ori(FileFolder,File)
        # Writing APDL Commands to assing elements orientation:
        Write_Local_Cood_APDL_temp_file(df)
        # Opening TexGen .eld arquive:
        df = Open_TexGen_eld(FileFolder,File)
        # Identifying Matrix and Fibers, and creating node components:
        Identify_Matrix_and_Fiber(df)

        return None


    def MountCdb(self,name='Default',folder='Default',ansys_exe_path='Default',ansysProd='Default'):
        '''
        Run Ansys in Bath, and save the cdb file. By default, it 
        save a cdb with a default name and in the Cdb's Directory (..\CDB Files). If the
        the directory doesn't exists, it is created. 
        '''
        from datetime import datetime
        from Solve import AnsysBath
        Solution = AnsysBath()

        if name =='Default':
            name = r"geo_macro_created" 
        if folder == 'Default':
            folder = r"{}\CDB Files".format(TellsCurrentDirectory())
            CheckIfFolderExists(folder)
        if not ansys_exe_path=='Default':
            if not type(ansys_exe_path)=='String':
                print("Please, the path must be a string")

            Solution.ChangeAnsysSolverParameters(['ANSYSexe'],[ansys_exe_path])

        if not ansysProd=='Default':
            if not type(ansys_exe_path)=='String':
                print("Please, the path must be a string")

            Solution.ChangeAnsysSolverParameters(['product'],[ansysProd])
    

        fi = open("macrosetup.temp","r")
        f_setput = fi.read()
        fi.close()

        fi = open("ansysmatinput.temp","r")
        f_material = fi.read()
        fi.close()

        fi = open("nodecood.temp", "r")
        f_node = fi.read() #saving the nodes_to_apdl data to a var
        fi.close()

        fi = open("elementconnect.temp", "r")
        f_ele = fi.read() #savinf the element_to_apdl data to a var 
        fi.close()

        fi = open("localcood.temp", "r")
        f_localcood = fi.read() 
        fi.close()

        fi = open("matinfo.temp", "r")
        f_mat = fi.read() 
        fi.close()    
        
        save_cdb_string = SaveCDB(name,folder)
        
        self.macro_directory = r"{}\Macros".format(TellsCurrentDirectory())

        f = open(r"{}\macro_inp_to_cdb.temp".format(self.macro_directory),"w")
        f.write("\n\n!*************************************")
        f.write('\n!MACRO SETUP')
        f.write(f_setput)
        f.write("\n\n!*************************************")
        f.write("\n\n!*************************************")
        f.write('\n!MATERIAL PROPERTIES INPUT')
        f.write(f_material)
        f.write("\n\n!*************************************")
        f.write("\n!NODES INPUT")
        f.write("\n!*************************************\n\n")
        f.write(f_node)
        f.write("SAVE")
        f.write("\n!*************************************")
        f.write("\n!ELEMENTS INPUT")
        f.write("\n!*************************************\n\n")
        f.write(f_ele)
        f.write("\nSAVE")
        f.write("\n\n!**************************************\n\n")
        f.write("\n!CREATING LOCAL COORDINATES")
        f.write("\n\n!**************************************\n\n")
        f.write(f_localcood)
        f.write("\nSAVE")
        f.write("\n\n!**************************************\n\n")
        f.write("\n!CREATING MATERIAL AND COMPONENTS")
        f.write("\n\n!**************************************\n\n")
        f.write(f_mat)
        f.write("\nSAVE")
        f.write("\n\n!**************************************\n\n")
        f.write("\n!SAVING CDB\n")
        f.write("\nALLSEL\n\n")
        f.write(save_cdb_string)
        f.write("\n\n!**************************************\n\n")
        f.close()

        #Changing the macroname to be executed by ansys.
        Solution.ChangeAnsysSolverParameters(['MacroName'],
        ['macro_inp_to_cdb.temp'])
        Solution.RunAnsys()

        return None


    def DeleteTempFiles(self,DeleteMacTemp='YES'):
        '''
        Method to delete temporary files. If the user wants, the macro used to generate
        the CDB is not deleted. 
        '''
        if DeleteMacTemp == 'YES':
            import os
            os.remove('{}\macro_inp_to_cdb.temp'.format(self.macro_directory))

        #Delete the other files
        DeleteTempFile()

        return None
         

