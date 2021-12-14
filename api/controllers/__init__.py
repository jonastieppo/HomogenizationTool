# %%
import json
import os
class databaseSearcher():

    def __findByName(self,name,jsonfile):
        '''
        Find material by Name
        '''
        self.ConvertToDict(jsonfile)

        if name in self.dict_data:
            print("ok")

    def __ConvertToDict(self,file):
        '''
        Convert json text to a dictionary
        '''
        with open(file) as txt:
            self.dict_converted = json.load(txt)


    def __privatemethod(self):
        print("Hello World")

Inst = databaseSearcher()


# %%
