from mongo import MongoDB, CBPEnv
from pickle import dump, load

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

def get_workflow():
    with MongoDB(CBPEnv.UAT) as mdb:
        query : dict = dict()
        query['year'] = 2026
        query['type'] = 'forecast'
        query['isFinal'] = True
        for wf in mdb.GetWorkflows(queryParams=query):
            print(wf['renovated'])
            break

def get_communities():
    with MongoDB(CBPEnv.UAT) as mdb:
        for comm in mdb.Communities:
            for i, j in comm.items():
                print(i)
            break

def main():
    get_communities()

if __name__ == "__main__":
    main()
    print("ALL DONE")
