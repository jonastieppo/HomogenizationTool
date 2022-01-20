# %%
'''
To run the tests, execute the following line:
in root directory directory

ptw -c --config .\api\tests\pytest.ini

And, in other terminal:

flask run
'''
#     unittest.main()
# %%
# content of test_class.py

import requests
from controllers import *


# print(database)
class TestClass:
        
    def routes(self):
        self.port = r'http://127.0.0.1:5000/'
        self.getmaterials_route = self.port+r"/api/getallmaterials"


    def test_api_get_route(self):
        self.routes()
        r = requests.get(url=self.getmaterials_route)
        print(r)
        assert r"2/2 twill E-glass woven fabric/epoxy" in r.json()

# %%
import pytest


def func(x):
    return x + 1


# def test_answer():
#     assert func(3) == 5