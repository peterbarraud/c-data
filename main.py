from mongo import MongoDB, CBPEnv
from pickle import dump, load
from dataclasses import fields
import datetime

from logger import Logger
from htmlbuilder import HtmlBuilder, Header, CellType
from infoclasses import WorkflowInfo, CommunityInfo
from nextbudgetversion import get_next_budget_status_version


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

def get_all_community_info(mdb : MongoDB):
    communityInfo : dict = dict()
    for community in mdb.Communities:
        communityInfo[community['communityId']] = CommunityInfo(community['communityName'],community['units']) 
    return communityInfo


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
        workflow_name_values : dict = get_workflow_name_values(mdb=mdb)
        
        processed_workflows : dict = dict()
        processed_status : dict = dict()
        for community_code, wfs in workflow_by_community.items():
            processed_workflow = None
            workflow_info = WorkflowInfo()
            final_wf_list = [wf for wf in wfs if wf['isFinal']]
            if final_wf_list:
                processed_workflow = final_wf_list[0]
                
            else:
                wf_dict = {wf['version']:wf for wf in wfs}
                max_version = max(wf_dict,key=wf_dict.get)
                processed_workflow = wf_dict[max_version]
            workflow_info.CommunitName = processed_workflow['communityName']
            workflow_info.Status = workflow_name_values[processed_workflow['status']]
            workflow_info.Version = str(processed_workflow['version'])
            workflow_info.StartDate = processed_workflow['startDate']
            workflow_info.EndDate = processed_workflow['endDate']
            workflow_info.Units = int(processed_workflow['units'])
            workflow_info.CommunitName = processed_workflow['communityName']
            if workflow_info.Status in processed_status:
                processed_status[workflow_info.Status] += 1
            else:
                processed_status[workflow_info.Status] = 1            
            processed_workflows[community_code] = workflow_info

        all_communities_info : dict = get_all_community_info(mdb=mdb)

        html = HtmlBuilder()

        html.InsertNewHeader(Header.H1,'Summary')
        

        table = html.NewTable({'border':1})

        tr = html.NewTableRow(tableToAppendTo=table)
        html.NewTableCell(CellType.TH,tr,'Total communities')
        html.NewTableCell(CellType.TH,tr,'Communties worked on')
        for process_stati in processed_status.keys():
            html.NewTableCell(CellType.TH,tr,process_stati)
        html.NewTableCell(CellType.TH,tr,'Not started')

        tr = html.NewTableRow(tableToAppendTo=table)
        html.NewTableCell(CellType.TD,tr,str(len(all_communities_info.keys())))
        html.NewTableCell(CellType.TD,tr,str(len(processed_workflows.keys())))
        for _, process_count in processed_status.items():
            html.NewTableCell(CellType.TD,tr,str(process_count))
        html.NewTableCell(CellType.TD,tr,f'{len(all_communities_info.keys())-len(processed_workflows.keys())}')

        html.InsertNewHeader(Header.H1,'Community details')

        table = html.NewTable({'border':1})

        tr = html.NewTableRow(tableToAppendTo=table)

        html.NewTableCell
        html.NewTableCell(CellType.TH,tr,"Community code")
        html.NewTableCell(CellType.TH,tr,"Community name")
        html.NewTableCell(CellType.TH,tr,"Status")
        html.NewTableCell(CellType.TH,tr,"Version")
        html.NewTableCell(CellType.TH,tr,"Start date")
        html.NewTableCell(CellType.TH,tr,"End date")
        html.NewTableCell(CellType.TH,tr,"Units")


        for community_id,community_info in all_communities_info.items():
            tr = html.NewTableRow(tableToAppendTo=table)
            # print(community_id,community__value)
            wf_info : WorkflowInfo = processed_workflows.get(community_id,False)
            html.NewTableCell(CellType.TD,tr,community_id)
            if wf_info:
                dates : dict = dict()
                for field in fields(wf_info):
                    if field.type == datetime.date:
                        html.NewTableCell(CellType.TD,tr,getattr(wf_info, field.name).strftime('%Y-%m-%d'))
                        dates[field.name] = getattr(wf_info, field.name)
                    else:
                        html.NewTableCell(CellType.TD,tr,getattr(wf_info, field.name))
                # html.NewTableCell(CellType.TD,tr,(dates['EndDate'] - dates['StartDate']).days)
            else:
                html.NewTableCell(CellType.TD,tr,community_info.Name)
                html.NewTableCell(CellType.TD,tr,'Not Started',4)
                html.NewTableCell(CellType.TD,tr,community_info.Units)
        html_file = f'D:/tech-stuff/cbp-data/testing.data/budget.status.v{get_next_budget_status_version()}.html'
        html.Save(html_file)
        print(f'Output here: {html_file}')



if __name__ == "__main__":
    x = get_next_budget_status_version()
    env : CBPEnv = CBPEnv.UAT
    print(f"We are in {env.name}")
    # get_communities(env)
    get_budget_status(env)
    # get_business_flows(env)
    print("ALL DONE")
