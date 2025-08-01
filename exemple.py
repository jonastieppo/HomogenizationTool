# %%

from Model_creation import TexGen_Mesh_to_cdb #Model Creation
from PBC_on_CDB import PeriodicCommandSetup # Periodic Boundary Conditions
from Uniform_Strain_Field_in_CDB import Non_Periodic_BC #UDBC
from Solve import AnsysBath #Solution with ansys
from PostProcessing import PostProcessing #Post Processing: Engineering Constants, etc.
from CLT import*
import os


Model = TexGen_Mesh_to_cdb() #Creating the model

#Assign Properties

E_glass_Vinylester_80 = {'E1':57.5E3,
                  'E2':18.8E3,
                  'G12':7.44E3,
                  'G23':7.26E3,
                  'v12':0.25,
                  'v23':0.29,
                  'vf':1,
                  'Name':'Vinylester derakane'
                    }

VinilEsterDerakane = {'E1':3.4E3,
                      'v12':0.34,
                      'Name':r'E-glass/Vinylester 80%'
                        }

Model.AssingnMaterial(Tow_Properties=E_glass_Vinylester_80,Matrix_Properties=VinilEsterDerakane)
MeshFolder = r"mesh"

# %%
# Changing the .exe location:

ansys_exe = r"C:\Program Files\ANSYS Inc\v241\ansys\bin\winx64\MAPDL.exe"

Model.TranslateTexGenFiles(FileFolder=MeshFolder,File='plain-weave')
Model.MountCdb(ansys_exe_path=ansys_exe)
# %%
Model.DeleteTempFiles()

# %%

BoundaryConditions = PeriodicCommandSetup()
# BoundaryConditions.Write_Macro(directory_to_save=f"{os.getcwd()}\\teste_case")
BoundaryConditions.Write_Macro()
BoundaryConditions.DeleteTempFiles()

Solution = AnsysBath()

# %%
# macro_name = 'macro_test.mac'
Solution.ChangeAnsysSolverParameters(['ANSYSexe'],[ansys_exe])
Solution.RunAnsys()

# %%
