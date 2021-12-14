# %%
from flask import Flask
from flask import request
import sys
import os
import json
# #Adding folders'
# controllersPath = f'{os.getcwd()}'+r'\controllers'
# sys.path.insert(0,controllersPath)

# THESIS MODULUS
from controllers.Model_creation import TexGen_Mesh_to_cdb #Model Creation
from controllers.PBC_on_CDB import PeriodicCommandSetup # Periodic Boundary Conditions
from controllers.Uniform_Strain_Field_in_CDB import Non_Periodic_BC #UDBC 
from controllers.Solve import AnsysBath #Solution with ansys
from controllers.PostProcessing import PostProcessing #Post Processing: Engineering Constants, etc. 
from controllers.CLT import*

# ROUTES

# %%
app = Flask(__name__)

@app.route('/api/getallmaterials')
def getallmaterials():
    return json.loads(json.dumps(ExperimentalResults()))

@app.route('/api/getallfibers')
def getallfibers():
    return "all fibers"

@app.route('/api/getallmatrix')
def getallmatrix():
    return "all matrix"

@app.route('/api/setmaterial', methods=['POST'])
def setmaterial():
    print(request.get_json())
    return "set material route"

if __name__=="__main__":
    app.run(port=4996, debug=True)
# app.run(port=4996)

# %%
