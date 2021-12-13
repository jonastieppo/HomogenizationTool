# # %%
# from flask import Flask
# import sys
# import os
# import json
# #Adding folders'
# controllersPath = f'{os.getcwd()}'+r'\controllers'
# sys.path.insert(0,controllersPath)

# from Model_creation import TexGen_Mesh_to_cdb #Model Creation
# from PBC_on_CDB import PeriodicCommandSetup # Periodic Boundary Conditions
# from Uniform_Strain_Field_in_CDB import Non_Periodic_BC #UDBC 
# from Solve import AnsysBath #Solution with ansys
# from PostProcessing import PostProcessing #Post Processing: Engineering Constants, etc. 
# from CLT import*

# app = Flask(__name__)

# @app.route("/")
# def teste():
#     # return json.loads(json.loads(json.dumps(ExperimentalResults())))
#     return "<h1>Heste</h1>"

# %%
from flask import Flask, escape, request

app = Flask(__name__)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'

# %%
