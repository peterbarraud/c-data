from mongo import MongoDB, CBPEnv
from pickle import dump, load
from logger import Logger
from dataclasses import dataclass

@dataclass
class WorkflowInfo:
    CommunitName : str
    Status : str
    Version : float

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

def get_communities(env : CBPEnv):
    log = Logger()
    with MongoDB(env) as mdb:
        for comm in mdb.Communities:
            for i, j in comm.items():
                log.Writeln(f"* {i}: {j}")
            break
    log.close()

def get_workflow_name_values(mdb : MongoDB):
    name_values : dict = dict()
    for i, j in mdb.BusinessFlows.items():
        name_values[i] = j['display']
    return name_values

def get_community_name_values(mdb : MongoDB):
    name_values : dict = dict()
    for community in mdb.Communities:
        name_values[community['communityId']] = community['communityName']
    return name_values

def get_budget_status(env : CBPEnv):
    """
    For a specific period (budget or forecast), get the workflow status of each community
    """
    with MongoDB(env=env) as mdb:
        community_name_values = get_community_name_values(mdb)
        # print(community_name_values)
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
        workflow_name_values : dict = get_workflow_name_values(mdb=mdb)
        log = Logger()
        processed_workflows : dict = dict()
        for community_code, wfs in workflow_by_community.items():
            workflow_info = WorkflowInfo(None,None,None)
            final_wf_list = [wf for wf in wfs if wf['isFinal']]
            if final_wf_list:
                final_wf = final_wf_list[0]
                workflow_info.CommunitName = final_wf['communityName']
                workflow_info.Status = workflow_name_values[final_wf['status']]
                workflow_info.Version = str(final_wf['version'])
            else:
                wf_dict = {wf['version']:wf for wf in wfs}
                max_version = max(wf_dict,key=wf_dict.get)
                workflow_info.CommunitName = wf_dict[max_version]['communityName']
                workflow_info.Status = workflow_name_values[wf_dict[max_version]['status']]
                workflow_info.Version = str(final_wf['version'])
            processed_workflows[community_code] = workflow_info

            # if the workflow has one isfinal, then we take that status
            # else we use the status of the highest version
            # for w in wfs:
            #     log.Writeln(w['isFinal'])
            # log.Writeln('*'*50)
        # print(processed_workflows)
        for community_name,community__value in get_community_name_values(mdb=mdb).items():
            print(community_name,community__value)
        log.close()


if __name__ == "__main__":
    env : CBPEnv = CBPEnv.UAT
    print(f"We are in {env.name}")
    # get_communities(env)
    get_budget_status(env)
    # get_business_flows(env)
    print("ALL DONE")
