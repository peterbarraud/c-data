from mongo import MongoDB, CBPEnv
from pickle import dump, load
from logger import Logger

def make_gl_document():
    gl_doc_file = open('gl.csv', 'w')
    mdb = MongoDB(CBPEnv.UAT)
    headerDoc = mdb.HeaderDocument
    glDoc = mdb.GLDocument
    # with open('temp.data/header.doc','rb') as f:
    #     headerDoc = load(f)
    # with open('temp.data/gl.doc','rb') as f:
    #     glDoc = load(f)
    for _, categoryDetails in headerDoc.items():
        # print(categoryDetails)
        gl_doc_file.write(f"{categoryDetails['title']},{categoryDetails['type']}\n")
        for headerDetails in categoryDetails['headers']:
            categoryID = headerDetails['control']
            gl_doc_file.write(f"{headerDetails['title']}\n")
            for gl in glDoc[categoryID]:
                gl_doc_file.write(f"{gl['view']},{gl['name']},{gl['code']},{gl['isActive']},{gl['isProvisioned']},{gl['type']}\n")

    gl_doc_file.close()

def get_workflow_instances():
    with MongoDB(CBPEnv.UAT) as mdb:
        for wf in mdb.WorkflowInstances:
            print(wf)
            break

def get_workflows():
    with MongoDB(CBPEnv.UAT) as mdb:
        query : dict = dict()
        query['year'] = 2024
        query['type'] = 'forecast'
        query['isFinal'] = True
        for wf in mdb.GetWorkflows(queryParams=query):
            for i, j in wf.items():
                print(i, j)
            break

def get_communities():
    log = open('logger.log', 'w')
    with MongoDB(CBPEnv.UAT) as mdb:
        for comm in mdb.Communities:
            for i, j in comm.items():
                log.write(f"* {i}: {j}\n")
            break
    log.close()


def get_budget_status(env : CBPEnv):
    """
    For a specific period (budget or forecast), get the workflow status of each community
    """
    with MongoDB(env=env) as mdb:
        # get workflows for a specific year and period
        # for testing, lets use a saved workflows
        # dict structure
        # key = _id
        # value = workflow
        workflow_Dict : dict = dict()
        # dict structure
        # key = community code
        # value = array of workflow dict (value of workflow_Dict)
        workflow_by_community : dict = dict()
        isTesting = True
        if isTesting:
            with open('testing.data/workflow.instances.obj', 'rb') as f:
                workflow_Dict = load(f)
        else:
            query : dict = dict()
            query['year'] = 2026
            query['type'] = 'budget'
            query['isDeleted'] = False
            for wf in mdb.GetWorkflows(queryParams=query):
                workflow_Dict[wf['_id']] = wf
            with open('testing.data/workflow.instances.obj', 'wb') as f:
                dump(workflow_Dict, f)
        for id, wf in workflow_Dict.items():
            community_code = wf['community']
            if community_code not in workflow_by_community:
                workflow_by_community[community_code] = list()
            workflow_by_community[community_code].append(wf)
        # print(workflow_by_community)
        log = Logger()
        for key_community_code, wfs in workflow_by_community.items():
            log.Writeln(key_community_code)
            version_list : list = list()
            for wf in wfs:
                if wf['isFinal']:
                    pass
                else:
                    version_list.append(wf['version'])

            # if the workflow has one isfinal, then we take that status
            # else we use the status of the highest version
            if any([w for w in wfs if w['isFinal']]):
                for wf in wfs:


                print(w['status'])
            else:
                pass
            # for w in wfs:
            #     log.Writeln(w['isFinal'])
            # log.Writeln('*'*50)
        log.close()

if __name__ == "__main__":
    env : CBPEnv = CBPEnv.UAT
    print(f"We are in {env.name}")
    get_budget_status(env)
    print("ALL DONE")
