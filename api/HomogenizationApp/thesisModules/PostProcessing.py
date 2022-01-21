'''
This Module will Search for the Results from Ansys, and perfrom some calculations.
'''

import pandas as pd 
import numpy as np
from time import perf_counter
from tqdm import tqdm

def PostProcessingInitialMessage():
    '''
    Prints Message for the user
    '''
    DefaultSeperatorTerminal()
    time = TellsDate()
    print(r"Starting Post-Processing Operations - {}".format(time))
    DefaultSeperatorTerminal()
    return None


def StrainCasesList():
    '''
    Just a method to return a list with the strain case (To be used in a loop). Yes, it is a little dumb,
    I've tried tu return 'DictionaryStrain' in StrainState method, but it lead to some erros, so I decided to be a little bit
    redundant here.
    '''
    DictionaryList = ['Exx','Eyy','Ezz','Exy','Eyz','Exz']
    
    return DictionaryList


def TellsCurrentDirectory():
    '''
    A method to tell the current directory
    '''
    import os
    directory = os.getcwd()
    return directory


def CalculateAvgSelectResults(results_folder,BoundaryConditions='ALL'):
    '''
    Method to Select the exit files from Ansys Results
    '''
    time_initial = perf_counter()
    if BoundaryConditions=='ALL':
        BoundaryConditions=StrainCasesList()

    def BoundaryConditionName(BoundaryCondition):
        '''
        Method that will receive a StrainCase, and return a pretty name
        '''
        BC_names = {'Exx':'Uniform Exx',
                    'Eyy':'Uniform Eyy',
                    'Ezz':'Uniform Ezz',
                    'Exy':'Uniform Exy',
                    'Eyz':'Uniform Eyz',
                    'Exz':'Uniform Exz'
                    }
        
        return BC_names[BoundaryCondition]
    
    print("Calculating the Strain and Stress Average...")
    data_AVG_strain_dictionary = {}
    data_AVG_stress_dictionary = {}    
    for BoundaryCondition in BoundaryConditions:
        StrainData = r"strainresults{}.temp".format(BoundaryCondition)
        StressData = r"stressresults{}.temp".format(BoundaryCondition)
        Avg_Strain_dictionary,Avg_Stress_dictionary=CalculateAvgStrainStress(results_folder,StrainData,StressData, sep = ',')
        BC_name = BoundaryConditionName(BoundaryCondition)
        data_AVG_strain_dictionary[BC_name]=Avg_Strain_dictionary
        data_AVG_stress_dictionary[BC_name]=Avg_Stress_dictionary

    AVG_Strain_Dataframe = pd.DataFrame(data = data_AVG_strain_dictionary)
    AVG_Stress_Dataframe = pd.DataFrame(data = data_AVG_stress_dictionary)

    time_final = perf_counter()
    time_elapsed = time_final-time_initial
    print(r"Strain and Stress Averages Calculated!( Time Elasped: {} s)".format(time_elapsed))
    DefaultSeperatorTerminal()

    return AVG_Strain_Dataframe,AVG_Stress_Dataframe


def DefaultSeperatorTerminal():
    '''
    Just a method to print a default separator in Terminal
    '''
    print("\n!------------------------------------------------!\n")

    return None


def CalculateAvgStrainStress(path,StrainData,StressData, sep = ','):
    '''
    Method to take the strain data over the volume, as the stress, and calculate the average. The dataframe
    separation,  by default, is done by commas. 

    Returns two dictionaries with Avg Strains and Stress of a given Boudary Condition Case
    '''

    full_path_strain = r"{}\{}".format(path,StrainData)
    full_path_stress = r"{}\{}".format(path,StressData)
    
    StrainDataFrame = pd.read_csv(full_path_strain,sep=sep)
    
    StressDataFrame = pd.read_csv(full_path_stress,sep=sep)
    
    dataframe_only_volume = StrainDataFrame['VOL']
    
    TotalVolume = dataframe_only_volume.sum()
    
    
    d1 = {'#Element': dataframe_only_volume, 'VOL': dataframe_only_volume, 'EXX': dataframe_only_volume, 'EYY': dataframe_only_volume,'EZZ': dataframe_only_volume,'EXY': dataframe_only_volume,'EYZ': dataframe_only_volume,'EXZ': dataframe_only_volume}
    d2 = {'#Element': dataframe_only_volume, 'VOL': dataframe_only_volume, 'SXX': dataframe_only_volume, 'SYY': dataframe_only_volume,'SZZ': dataframe_only_volume,'SXY': dataframe_only_volume,'SYZ': dataframe_only_volume,'SXZ': dataframe_only_volume}
    volume_dataframe_all_columns_strain = pd.DataFrame(data=d1) 
    volume_dataframe_all_columns_stress = pd.DataFrame(data=d2)
    
    Strain_multiplied_by_volumes = StrainDataFrame.multiply(volume_dataframe_all_columns_strain)
    Stress_multiplied_by_volumes = StressDataFrame.multiply(volume_dataframe_all_columns_stress)
    
    sum_of_Strain_multiplied_by_volumes = Strain_multiplied_by_volumes.sum()
    sum_of_Stress_multiplied_by_volumes = Stress_multiplied_by_volumes.sum()
    
    Exx_avg = sum_of_Strain_multiplied_by_volumes['EXX']/TotalVolume
    Eyy_avg = sum_of_Strain_multiplied_by_volumes['EYY']/TotalVolume
    Ezz_avg = sum_of_Strain_multiplied_by_volumes['EZZ']/TotalVolume
    Exy_avg = sum_of_Strain_multiplied_by_volumes['EXY']/TotalVolume
    Eyz_avg = sum_of_Strain_multiplied_by_volumes['EYZ']/TotalVolume
    Exz_avg = sum_of_Strain_multiplied_by_volumes['EXZ']/TotalVolume
    
    Sxx_avg = sum_of_Stress_multiplied_by_volumes['SXX']/TotalVolume
    Syy_avg = sum_of_Stress_multiplied_by_volumes['SYY']/TotalVolume
    Szz_avg = sum_of_Stress_multiplied_by_volumes['SZZ']/TotalVolume
    Sxy_avg = sum_of_Stress_multiplied_by_volumes['SXY']/TotalVolume
    Syz_avg = sum_of_Stress_multiplied_by_volumes['SYZ']/TotalVolume
    Sxz_avg = sum_of_Stress_multiplied_by_volumes['SXZ']/TotalVolume
    
    Strains_avg_dict = {
    
        'Exx':Exx_avg,
        'Eyy':Eyy_avg,
        'Ezz':Ezz_avg,
        'Exy':Exy_avg,
        'Eyz':Eyz_avg,
        'Exz':Exz_avg
    }
    
    Stress_avg_dict = {
    
        'Sxx':Sxx_avg,
        'Syy':Syy_avg,
        'Szz':Szz_avg,
        'Sxy':Sxy_avg,
        'Syz':Syz_avg,
        'Sxz':Sxz_avg
    }
    return Strains_avg_dict,Stress_avg_dict


def TellsDate():
    '''
    Method to tells the date. Returns a string
    '''
    import datetime

    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d %H:%M:%S")

    return date


def CalculateCompliance(StrainAvgDict,StressAvgDict):
    '''
    Method to calculate compliance and stiffness matrix. The input arguments are two
    dictionaries: the strain average at each strain state aplication, and the Stress Stave Average with
    each strain state application.
    '''
    # input("Press Enter...")
    df_strain = pd.DataFrame(data = StrainAvgDict)
    df_stress = pd.DataFrame(data = StressAvgDict)

    COF = np.zeros((36,36))

    StressVector = np.zeros((36,1))

    for i in range(0,6):
        for j in range(0,6):
            for k in range(0,6):
                #if k == i:
                COF[6*i+j,6*j+k] = df_strain.iloc[k,i]
                #if k != i:
                 #   COF[6*i+j,6*j+k] =0

    def printCOF(m):
        f=  open("CHECKCOFT.temp",'w')
        for i in range(0,36):
            for j in range(0,36):
                f.write("\t{0:8.5e}".format(m[i,j])) 
            f.write("\n")
        f.close()

    #printCOF(COF)

    #Defining a function that will concatened a dataframe, by it columns
    def ConcaColumns(dataframe):
        #size = dataframe.shape[0]*dataframe.shape[1]
        #c = np.zeros((size,1))
        c = []
        for i in range(dataframe.shape[1]):
           # c[:,0] = dataframe.iloc[:,i]
           c = np.append(c,dataframe.iloc[:,i], axis = 0)
        return c


    StressVector = ConcaColumns(df_stress)

    solution = np.linalg.solve(COF,StressVector)

    Stiffness = np.zeros((6,6))

    count = 0
    for i in range(0,6):
        for j in range(0,6):
            Stiffness[i,j]=solution[count,]
            count=count+1
    

    Compliance = np.linalg.inv(Stiffness)

    df_stiff = pd.DataFrame(Stiffness)
    df_compliance = pd.DataFrame(Compliance)

    Compliance = df_compliance
    Stiffness = df_stiff

    return Compliance,Stiffness


def CalculateCalculateEngineeringConstants(ComplianceMatrix):
    '''
    Method to calculate the Engineering Constants
    '''
    df = pd.DataFrame(ComplianceMatrix)
    
    E1 = 1/df.iloc[0,0]
    E2 = 1/df.iloc[1,1]
    E3 = 1/df.iloc[2,2]
    G12 = 1/df.iloc[3,3]
    G23 = 1/df.iloc[4,4]
    G31 = 1/df.iloc[5,5]

    v21 = -E2*df.iloc[0,1]
    v31 = -E3*df.iloc[0,2]
    eta1_12 = G12*df.iloc[0,3]
    eta_23 = G23*df.iloc[0,4]
    eta1_31 = G31*df.iloc[0,5]

    v12 = -E1*df.iloc[1,0]
    v32 = -E3*df.iloc[1,2]
    eta2_12 = G12*df.iloc[1,3]
    eta2_23 = G23*df.iloc[1,4]
    eta2_31 = G31*df.iloc[1,5]

    v13 = -E1*df.iloc[2,0]
    v23 = -E2*df.iloc[2,1]
    eta3_12 = G12*df.iloc[2,3]
    eta3_23 = G23*df.iloc[2,4]
    eta3_31 = G31*df.iloc[2,5]

    eta12_1 = E1*df.iloc[3,0]
    eta12_2 = E2*df.iloc[3,1]
    eta12_3 = E3*df.iloc[3,2]
    mi12_23 = G23*df.iloc[3,4]
    mi12_31 = G31*df.iloc[3,5]

    eta23_1 = E1*df.iloc[4,0]
    eta23_2 = E2*df.iloc[4,1]
    eta23_3 = E3*df.iloc[4,2]
    mi23_12 = G12*df.iloc[4,3]
    mi23_31 = G23*df.iloc[4,5]

    eta31_1 = E1*df.iloc[5,0]
    eta31_2 = E2*df.iloc[5,1]
    eta31_3 = E3*df.iloc[5,2]
    mu31_12 = G12*df.iloc[5,3]
    mi31_23 = G23*df.iloc[5,4]

    EngineeringConstants = {
        "E1": E1,
        "E2": E2,
        "E3" : E3,
        "G12" : G12,
        "G23" : G23,
        "G31" : G31,
        "v21" : v21,
        "v31" : v31,
        "eta1_12" : eta1_12,
        "eta_23" : eta_23,
        "eta1_31" : eta1_31,
        "v12" : v12,
        'v32' : v32,
        'eta2_12' : eta2_12,
        'eta2_23' : eta2_23,
        'eta2_31' : eta2_31,
        'v13' : v13,
        'v23' : v23,
        'eta3_12' : eta3_12,
        'eta3_23' : eta3_23,
        'eta3_31' : eta3_31,
        'eta12_1' : eta12_1,
        'eta12_2' : eta12_2,
        'eta12_3' : eta12_3,
        'mi12_23' : mi12_23,
        'mi12_31' : mi12_31,
        'eta23_1' : eta23_1,
        'eta23_2' : eta23_2,
        'eta23_3' : eta23_3,
        'mi23_12' : mi23_12,
        'mi23_31' : mi23_31,
        'eta31_1' : eta31_1,
        'eta31_2' : eta31_2,
        'eta31_3' : eta31_3,
        'mu31_12' : mu31_12,
        'mi31_23' : mi31_23
    }
    
    return EngineeringConstants


def Correct_Compliance_and_Stiffness(factor,ComplianceMatrix,StiffnessMatrix):
    '''
    Method that receives the  Compliance and Stiffness matrices, and 
    returns a the respective value corrected. A more accurate method can 
    be added after. 
    '''

    Compliance_corrected = ComplianceMatrix*(1/factor)
    Stiffness_corrected = StiffnessMatrix*factor

    return Compliance_corrected,Stiffness_corrected

def CalculateMatrixNorm(dataframe):
    '''
    Method to calculate a norm of a matrix
    '''
    matrix = dataframe.to_numpy()

    from numpy import linalg as LA

    MatrixNorm = LA.norm(matrix)

    return MatrixNorm

class PostProcessing():
    '''
    This class will read the saved results and rules some calculations. 
    '''
    def __init__(self,results_folder = 'Default',BoundaryConditions='ALL'):
        '''
        This method will open the results from Ansys Calculates the Avegerage Stress and Strains in the domain.
        '''  
        if results_folder == 'Default':
            results_folder = TellsCurrentDirectory()
            results_folder = r"{}\Results".format(results_folder)

        PostProcessingInitialMessage()
        self.AVG_Strain_Dataframe, self.AVG_Stress_Dataframe=CalculateAvgSelectResults(results_folder)

        if BoundaryConditions=='ALL':
            DefaultSeperatorTerminal()
            print("Calculating Compliance and Stiffness Matrix...")       
            self.Compliance,self.Stiffness = CalculateCompliance(self.AVG_Strain_Dataframe,self.AVG_Stress_Dataframe)
            print("Done!")
            DefaultSeperatorTerminal()

            self.EngineeringConstants = None
       
        return None  


    def ShowMeanStress(self):
        '''
        A method that will print the Stress Avg Result
        '''
        DefaultSeperatorTerminal()
        print("Stress Results: (Columns are BC and lines are the AVG Stress)")
        print(self.AVG_Stress_Dataframe)
        DefaultSeperatorTerminal()

        return None


    def ShowMeanStrain(self):
        '''
        Method to print the Avg Strain dataframe Calculated
        '''
        DefaultSeperatorTerminal()
        print("Strain Results: (Columns are BC and lines are the AVG Strains)")
        print(self.AVG_Strain_Dataframe)
        DefaultSeperatorTerminal()

        return None


    def ShowCompliance(self):
        '''
        A method to print compliance matrix.
        '''
        DefaultSeperatorTerminal()
        print("Compliance Matrix:")
        print(self.Compliance)
        DefaultSeperatorTerminal()

        return None


    def ShowStiffness(self):
        '''
        A method to print stiffness matrix
        '''
        DefaultSeperatorTerminal()
        print("Stiffness Matrix:")
        print(self.Stiffness)
        DefaultSeperatorTerminal()

        return None


    def ExportCompliance(self):
        '''
        Just a method to print the Compliance
        '''
        DataFrame = self.Compliance
        DataFrame.to_csv('compliance.out',sep='\t', header = None, index = False)


    def CalculateEngConstants(self):
        '''
        Method to calculate Engineering Constants
        '''
        DefaultSeperatorTerminal()
        print("Calculating Engineering Constants...")
        self.EngineeringConstants = CalculateCalculateEngineeringConstants(self.Compliance)        
        print("Done!")
        DefaultSeperatorTerminal()

        return None


    def ExportStiffness(self):
        '''
        Just a method to print the stiffness
        '''
        DataFrame = self.Stiffness
        DataFrame.to_csv('stiffness.out',sep='\t', header = None, index = False)
        

    def ShowEngineeringConstants(self,Property='ALL'):
        '''
        A method to return the engineering constants when requested. The property can be a valid string,
        or list of valid Strings. It returns a dictionary with all the request values
        '''

        if self.EngineeringConstants == None:
            print("There are no Eng. Constants to show!")
            print("Runs the  method CalculateEngConstants()!")
            print("Calculating Engineering Constants, anyway...")
            self.EngineeringConstants = CalculateCalculateEngineeringConstants(self.Compliance)  
            print("Done!")
            DataFrameForBetterVisualization = pd.DataFrame(data = {'Engineering Const. Value':self.EngineeringConstants})

            return DataFrameForBetterVisualization

        if Property=='ALL':
        
            DataFrameForBetterVisualization = pd.DataFrame(data = {'Engineering Const. Value':self.EngineeringConstants})

            print("Requested Engineering Constants (Default = 'ALL'):")            
            print(DataFrameForBetterVisualization)
            
            return DataFrameForBetterVisualization
    
        else:
            EngineeringConstantsOutPutDictionary = {}
            for EngineeringRequest in Property:
                EngineeringConstantsOutPutDictionary[Property]=self.EngineeringConstants[EngineeringRequest]
            
            DataFrameForBetterVisualization = pd.DataFrame(data = {'Engineering Const. Value':EngineeringConstantsOutPutDictionary})
            print("Requested Engineering Constants {}:".format(Property))            
            print(DataFrameForBetterVisualization)
            
            return DataFrameForBetterVisualization
        
        
    def ShowEngineeringConstantsCorrected(self,factor):
        '''
        Method to show the engineering constants already corrected. 
        '''
        #First, recalculate the compliance
        DefaultSeperatorTerminal()
        print("Calculating the Compliance and Stiffness matrix corrected:")
        self.ComplianceCorrected,self.StiffnessCorrected = Correct_Compliance_and_Stiffness(factor,self.Compliance,self.Stiffness)
        print("Done!")
        print("Calculating Engineering Constants:")
        self.EngineeringConstantsCorrected = CalculateCalculateEngineeringConstants(self.ComplianceCorrected)
        print("Done!") 
        DataFrameForBetterVisualization = pd.DataFrame(data = {'Engineering Const. Value (corrected):':self.EngineeringConstantsCorrected})

        return DataFrameForBetterVisualization

    def GetComplianceNorm(self):
        '''
        Method to return the norm of the Compliance
        '''
        print("Calculating the Compliance norm")
        norm = CalculateMatrixNorm(self.Compliance)
        print("Norm is {}".format(norm))

        return norm

    def GetStiffnessNorm(self):
        '''
        Method to to return the norm of the Stiffness
        '''
        print("Calculating the Stiffness norm")
        norm = CalculateMatrixNorm(self.Stiffness)
        print("Norm is {}".format(norm))

        return norm
    