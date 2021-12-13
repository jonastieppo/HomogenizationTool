
# %%

from Model_creation import TexGen_Mesh_to_cdb #Model Creation
from PBC_on_CDB import PeriodicCommandSetup # Periodic Boundary Conditions
from Uniform_Strain_Field_in_CDB import Non_Periodic_BC #UDBC 
from Solve import AnsysBath #Solution with ansys
from PostProcessing import PostProcessing #Post Processing: Engineering Constants, etc. 
from CLT import*
import os 
# %% 
'''
The process will be simple. The first step will be:

1) Create a geometry file, will all nodes and elements following a mesh created by TexGen; 
  1.a) This model will contain the material properties 
  1.b) The sequence of commands will be something like this:

    Model = TexGen_Mesh_to_cdb() #Creating the model
    Model.AssingnMaterial(Tow_Properties=E_glass_Vinylester_80,Matrix_Properties=VinilEsterDerakane)
    Model.TranslateTexGenFiles(FileFolder=MeshFolder,File='{}'.format('mesh'))
    Model.MountCdb()
    Model.DeleteTempFiles()

2) Apply Boundary Conditions, that will be from two type:

  2.a) Choose the boundary Conditions type
  2.b) Write an ansys macro

  The commands will be something like this:

  BoundaryConditions = PeriodicCommandSetup()
  BoundaryConditions.Write_Macro()
  BoundaryConditions.DeleteTempFiles()

3) Change macro name and job name

  3.a) In order to organize the results, just save the macro name and job name with different names. Also, save the results in different folder. 

'''

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
MeshFolder = r"C:\Users\Jonas\OneDrive - Universidade Federal do Rio Grande do Sul\Masters\Masters\Thesis\Thesis Cases - Texgen\plain-weave"

# %%
# Changing the .exe location:

ansys_exe = r"C:\Program Files\ANSYS Inc\v181\ansys\bin\winx64\MAPDL.exe"

Model.TranslateTexGenFiles(FileFolder=MeshFolder,File='simple_mesh')
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
# Solve all files 

# %%
# Post-processing - Read results, and save them in a location


# %%
# Run the same cases with CLT