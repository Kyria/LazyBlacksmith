# -*- encoding: utf-8 -*-
from enum import Enum


class ActivityEnum(Enum):
    """ Industry activity enum """
    NONE = (0, 'None')
    MANUFACTURING = (1, 'Manufacturing')
    RESEARCH_TIME_EFFICIENCY = (3, 'Time efficiency')
    RESEARCH_MATERIAL_EFFICIENCY = (4, 'Material efficiency')
    COPYING = (5, 'Copy')
    INVENTION = (8, 'Invention')
    REACTIONS = (11, 'Reactions')

    def __init__(self, id, label):
        self.id = id
        self.label = label
        

class BlueprintEnum(Enum):
    """ Identify the "blueprint" type between bpo, bpc, reaction, relics """
    
    NOTABLUEPRINT = 0
    REACTION = 1
    RELIC = 2
    BPC = 3
    BPO = 4
    
