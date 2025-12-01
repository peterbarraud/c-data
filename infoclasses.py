from dataclasses import dataclass
from datetime import date

@dataclass
class WorkflowInfo:
    CommunitName : str = None
    Status : str = None
    Version : float = None
    StartDate : date = None
    EndDate : date = None
    Units : int = None

@dataclass
class CommunityInfo:
    Name : str = None
    Units : int = 0
