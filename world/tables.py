from dataclasses import dataclass

def attribute_modifier_tbl():
    return {
        range(3,4): -2,    # 3
        range(4, 8): -1,     # 4-7
        range(8, 14): 0,    # 8-13
        range(14, 18): 1,   # 14-17
        range(18, 19): 2    # 18
    }

def background_tbl():
    return {
        1: "Barbarian",
        2: "Clergy",
        # 3: "Courtesan",
        # 4: "Criminal",
        # 5: "Dilettante",
        # 6: "Entertainer",
        # 7: "Merchant",
        # 8: "Noble",
        # 9: "Official",
        # 10: "Peasant",
        # 11: "Physician",
        # 12: "Pilot",
        # 13: "Politician",
        # 14: "Scholar",
        # 15: "Soldier",
        # 16: "Spacer",
        # 17: "Technician",
        # 18: "Thug",
        # 19: "Vagabond",
        # 20: "Worker"
    }


def lookup(value, table_func):
    tbl=table_func()
    for key_range, result in tbl.items():
        if value in key_range:
            return result
    return None


class Background:
    def __init__(self, name, description, **kwargs):

        self.name = name
        self.description = description
        
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        attrs = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return f"Background({', '.join(attrs)})"


@dataclass
class ModPoint:
    value: int
    stat: str



background=[Background("Barbarian"
           , "Barbarian skills"
           , free_skill=["Survive"]
           , quick_skills=["Surive","Notice","Any-Combat"]
           , growth = [ModPoint(1,"Any Stat"),
                       ModPoint(2,"Physical"),
                       ModPoint(2,"Physical"),
                       ModPoint(2,"Mental"),
                       ModPoint(1,"Exert"),
                       ModPoint(1,"Any Skill"),
                       ]
            , learning=[ModPoint(1,"Any Combat"),
                        ModPoint(1,"Connect"),
                        ModPoint(1,"Exert"),
                        ModPoint(1,"Lead"),
                        ModPoint(1,"Notice"),
                        ModPoint(1,"Punch"),
                        ModPoint(1,"Sneak"),
                        ModPoint(1,"Survive"),
            ]
           ),
           Background("Clergy"
           , "Clergy skills"
           , free_skill=["Talk"]
           , quick_skills=["Talk","Perform","Know"]
           , growth = [ModPoint(1,"Any Stat"),
                       ModPoint(2,"Mental"),
                       ModPoint(2,"Physical"),
                       ModPoint(2,"Mental"),
                       ModPoint(1,"Connect"),
                       ModPoint(1,"Any Skill"),
                       ]
            , learning=[ModPoint(1,"Administer"),
                        ModPoint(1,"Connect"),
                        ModPoint(1,"Know"),
                        ModPoint(1,"Lead"),
                        ModPoint(1,"Notice"),
                        ModPoint(1,"Perform"),
                        ModPoint(1,"Talk"),
                        ModPoint(1,"Talk"),
            ]
           ),           
           
           ]