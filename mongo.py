import pymongo
from enum import Enum
from json import load

class CBPEnv(Enum):
    PROD = 1
    UAT = 2

class MongoDB:
    def __init__(self, env : CBPEnv):
        connection_str : str = MongoDB.get_connection_string(env)
        self.mongo_client = pymongo.MongoClient(connection_str)
        self.mdb = self.mongo_client.get_database("test")

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.mongo_client.close()

    @staticmethod
    def get_connection_string(env : CBPEnv):
        f = open('connect.str.json')
        connection__info = load(f)
        f.close()
        return connection__info[env.name]


    def Close(self):
        self.mongo_client.close()

    @property    
    def Collections(self):
        """
            Returns a Cursor of Mongo collections
            You're going to have to iterate through this to get a specific collection 
            Example
            for c in Collections:
                print(c['name])
        """
        return self.mongo_db.list_collections()
    
    @property
    def GLDocument(self):
        return self.mdb.get_collection('tenant_gls').find().next()['glCodes']
    
    @property
    def HeaderDocument(self):
        return self.mdb.get_collection('tenant_headers').find().next()['headerCategories']
    
    @property
    def WorkflowInstances(self):
        """
        Workflow instance is the complete data for one workflow instance
        All the data as in all the values for all the individual drivers / gls for all months of that workflow instance
        """
        return self.mdb.get_collection('workflowinstances').find()
    
    def GetWorkflows(self,**queryParams):
        """
        Gets workflows based on the query parameters given
        This (I think) is actually a workflow insance but with the Metadata

        A workflow instance has all the CM/RA entered data
        """
        # return self.mdb.get_collection('workflows').find({'year':2024,'type':'forecast','isFinal':True})
        return self.mdb.get_collection('workflows').find(queryParams['queryParams'])
    
    @property
    def Communities(self):
        """
        Gets all the Communities
        """
        return self.mdb.get_collection("communities").find({})
        
    
    