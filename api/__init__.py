# %%
from flask import Flask
import sys
import os
import json
# #Adding folders'
# controllersPath = f'{os.getcwd()}'+r'\controllers'
# sys.path.insert(0,controllersPath)

from controllers.Model_creation import TexGen_Mesh_to_cdb #Model Creation
from controllers.PBC_on_CDB import PeriodicCommandSetup # Periodic Boundary Conditions
from controllers.Uniform_Strain_Field_in_CDB import Non_Periodic_BC #UDBC 
from controllers.Solve import AnsysBath #Solution with ansys
from controllers.PostProcessing import PostProcessing #Post Processing: Engineering Constants, etc. 
from controllers.CLT import*


# %%
app = Flask(__name__)

@app.route('/')
def index():
    return json.loads(json.dumps(ExperimentalResults()))

# app.run(port=4996)



# %%
