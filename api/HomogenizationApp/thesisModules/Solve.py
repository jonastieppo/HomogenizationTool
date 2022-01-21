# %%
'''
This module will define methods to run ansys in bath, once it shares the same inputs with several programs
'''
import pandas as pd 
import numpy as np
from time import perf_counter
from tqdm import tqdm

def CheckIfFolderExists(folder_to_check):
    '''
    Method that will receive a folder path, and check if it exists. If don't, create it
    '''
    import os
    if not os.path.exists(folder_to_check):
        os.makedirs(folder_to_check)

    return None


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


def AnsysDefaultParameters(AnsysWorkingDirectory='Default',outputAnsys='Default',macroName='Default',macroFolder='Default'):
    '''
    Method just to set the default parameters value
    '''

    from datetime import datetime

    if AnsysWorkingDirectory=='Default':
        wd = r"{}\Ansys WD".format(TellsCurrentDirectory())
        CheckIfFolderExists(wd) #If the folder doesn't exist, it is created

    if outputAnsys=='Default':
        output_root = r"{}\Ansys WD".format(TellsCurrentDirectory())
    if macroName=='Default':
        macroName = 'macro_to_solve'
    if macroFolder=='Default':
        macroFolder = r"{}\Macros".format(TellsCurrentDirectory())
        CheckIfFolderExists(macroFolder) #if the folder doesn't exists, it is created

    DictAnsysParametersDefult = {
        
        'ANSYSexe':r"C:\Program Files\ANSYS Inc\v190\ansys\bin\winx64\MAPDL.exe",
        'np':2,
        'WDpath':r"{}".format(wd),
        'jobname':'New Analysis',
        'memoryTotal':8000,
        'MacroPath':r'{}'.format(macroFolder),
        'MacroName':'{}.mac'.format(macroName),
        'outputPath':r"{}\file.out".format(output_root),
        'product':'ansys'
    }
    
    return DictAnsysParametersDefult


def ShowDefaultParameters(AnsysDefaultParameters):
    '''
    Method to print the default parameters. Returns None. Prints a dataframe

    The method receives the method AnsysDefaultParameres as input. 
    '''
    DictionaryWithInfo = AnsysDefaultParameters

    data = {"Default Parameters":DictionaryWithInfo}

    dataframe = pd.DataFrame(data=data)

    print("\nThe solver will use the following default parameters:")
    print("Use the method ChangeAnsysSolverParameters() to change it.")
    print("To check parameters explanation, use the method SolverInitialParametersExplanation()")
    DefaultSeperatorTerminal()
    print("                    DEFAULT PARAMETERS                       ")
    DefaultSeperatorTerminal()
    print(dataframe)

    return None


def RunAnsys_bath(AnsysParameters):
    
    '''
    Method that wull receive a dictionary with paramaters to be input in analisys
    '''

    import os
    import subprocess
    
    
    ANSYSexe = AnsysParameters['ANSYSexe']
    np = AnsysParameters['np']
    WDpath = AnsysParameters['WDpath']
    jobname = AnsysParameters['jobname']
    memoryTotal = AnsysParameters['memoryTotal']
    MacroPath = AnsysParameters['MacroPath']
    MacroName = AnsysParameters['MacroName']
    outputPath = AnsysParameters['outputPath']
    product = AnsysParameters['product']
    
    
    cmd =  (r'"{}"  -p {} -np {} -lch -dir "{}" -j "{}" -s read -m {} -db 1024 -l en-us -b -i "{}\{}" -o "{}"'.format(ANSYSexe,
                                                                                                                    product,
                                                                                                                    np,
                                                                                                                    WDpath,
                                                                                                                    jobname,
                                                                                                                    memoryTotal,
                                                                                                                    MacroPath,
                                                                                                                    MacroName,
                                                                                                                outputPath))
    
    print("Starting Ansys Runner:")

    print("Command Used:")
    print(cmd)
    
    outputrun = subprocess.call(cmd,shell = True)
    
    return outputrun


def AnsysSolverParametersExplanation():
    '''
    Just a solver to return a standarzided parameters names used to run ansys in bath mode.
    It returns, as usual, a dictionary. Again, it seems to be dumb, but it may prevent erros. It contains a 
    short explanation of each input parameter. 
    '''
    DictAnsysParametersExplanation = {
        
        'ANSYSexe':'Set the ansys APDL exe complete path.',
        'product':'Ansys Product to run',
        'np':'Number of processors (threads, in a strict way) to be used',
        'WDpath':'Working Directory where ansys should be run',
        'jobname':'Just set your desired Job Name',
        'memoryTotal':'Initial database memory to be reserved, in MB',
        'MacroPath':'Path where the ansys macro is saved',
        'MacroName':'Macro Name to be executed',
        'outputPath':'Full output path (that is, include the archive name)'
    }
    
    return DictAnsysParametersExplanation


def AnsysSolverParameterAccess(OldDictionary,Parameter,value):
    '''
    Method that will change the requested paramater, one by time. 
    '''
    count=0
    for Parameter_i in Parameter:
        OldDictionary[Parameter_i]=value[count]
        count=count+1
    
    return OldDictionary


def SolverInitialParametersExplanation():
        
        ExplanationDictionary = AnsysSolverParametersExplanation()
        data = {'Paramater Explanation':ExplanationDictionary}
        ParametersExplanation  = pd.DataFrame(data=data)
        print("Choose one of the parameters:")
        print(ParametersExplanation)
        
        return None

def DeleteTempFiles():
    '''
    Method to dele all temporary files
    '''
    import os
    import fnmatch
    current_path = TellsCurrentDirectory()

    for file_name in os.listdir(current_path):
        if fnmatch.fnmatch(file_name, '*.tmp'):
            os.remove(file_name)
        if fnmatch.fnmatch(file_name, '*.temp'):
            os.remove(file_name)
    print("All temporary files removed!")
    return None
class AnsysBath():


    def __init__(self,BathParameters='Default'):

        if BathParameters =='Default':
            self.CurrentParameters = AnsysDefaultParameters(AnsysWorkingDirectory='Default',outputAnsys='Default',macroName='Default',macroFolder='Default')


    def ExplainAnsysParameters(self):
        '''
        Method to Explain the default parameters to be used in analysis!
        '''
        DefaultSeperatorTerminal()
        print("Default Parameters Explanation:")
        SolverInitialParametersExplanation()
        DefaultSeperatorTerminal()
        ShowDefaultParameters(AnsysDefaultParameters())
        DefaultSeperatorTerminal()

        return None
    

    def ChangeAnsysSolverParameters(self,parametersnames,values):
        '''
        A method to change the parameters used to run ansys in bath mode.
        'parametersnames' may be be a string or a list of strings. 
        '''
        
        self.CurrentParameters = AnsysSolverParameterAccess(self.CurrentParameters,parametersnames,values)
        
        return 'Ansys Parameters Changed'


    def RunAnsys(self):
        '''
        Method to run Ansys In bath mode.  
        '''
        #First, lets delete all temp files
        # DeleteTempFiles()
        print("---------------------------------")
        print("\n!RUNNING ANSYS!")
        perf_counter_init = perf_counter()
        RunAnsys_bath(self.CurrentParameters)
        perf_counter_end = perf_counter()
        elapsed_time = perf_counter_end-perf_counter_init
        print("Elapsed Time in Analisys: {}".format(elapsed_time))


