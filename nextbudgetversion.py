from os import listdir
from re import search as research
from os import listdir

def get_next_budget_status_version():
    files_in_dir = listdir(r'testing.data')
    return max([int(research('budget.status.v([\d]+)\.html',x).groups()[0]) for x in files_in_dir if str(x).startswith('budget.status.v')])
