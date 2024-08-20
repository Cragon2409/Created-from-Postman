import math
from random import randrange,choice
from helpers import *
from tank_details import *
from constants import *

"""
============INTRO FUNC============
Called when the bot is first made, and whenever the tank evolves into a new type.
Given:
    - self : Bot(Tank)
    - tank_type : String
Outputs:
    - None
Effects:
    - Decide to have auto fire on or off by default if required
    - Decide a default self.follow_move_code if required
    - Set up other needed constants

    
============CHOOSE EVOLUTION PATH FUNC============
Called when the bot is made, pre-decides the evolution path.
Given:
    - starting_from="Basic" : String
Outputs:
    - evolution_path : List(String)
Effects:
    - None

    
============CHOOSE UPGRADE LEVELS FUNC============
Called when the bot is made, pre-decides the stat upgrades that will be taken at each level.
Given:
    - evolution_path : List(String)
Outputs:
    - upgrade_path
Effects:
    - level_upgrades


============UPDATE FUNC============
Called every frame, lets the bot decide what to do.
Given:
    - self : Bot(Tank)
    - ticks: int
Outputs: 
    - None
Effects: 
    -choose a direction to give to tank.accelerate() (must convert to unit vector first)
    -assign self.follow_move_code, self.follower_move_pos
    -call self.faceTowards(pos) to orient tank 
    -decide to fire or enable/disable autofire

"""

#helper function to assign a position as a pathfinding target
class DummyPosition: #dummy position object made for bot AI code
    DRAW_CODE = DRW_NONE
    def __init__(self,pos):
        self.pos = pos
        self.vel = [0,0]

def get_nearby(self): return list(filter(lambda x: x != self and (x.DRAW_CODE in [DRW_FOOD, DRW_TANK_BOT, DRW_TANK_PLR]) and ( (not x.DRAW_CODE in TANK_CODES) or x.team == TEAM_NULL or x.team != self.team), self.game.chunkManager.getInRect(dA(self.pos, BOT_VIEW_RECT[:2]), dS(self.pos, BOT_VIEW_RECT[:2]))))

###============== INTRO ==============###
"""
Intro func gets called when the tank is first initialised. Gets called after evolve and before upgrade assignments.
"""
def basic_init(self):
    self.auto_fire = False
    self.follow_move_code = 0

MID_ATTACK_DIST = 150
LONG_ATTACK_DIST = 250
SUM_ATTACK_DIST = 300
def type_check_init(self):
    final_type = self.evolve_path[-1]
    if (final_type in PSUEDO_MELEE_TYPES and randrange(0,100) <= 20) or final_type in MELEE_TYPES: 
        self.end_attack_type = "MELEE"
        self.chase_distance = 0
    elif final_type in MID_RANGER_TYPES: 
        self.end_attack_type = "MID"
        self.chase_distance = MID_ATTACK_DIST
    elif final_type in LONG_RANGER_TYPES: 
        self.end_attack_type = "LONG"
        self.chase_distance = LONG_ATTACK_DIST
    elif final_type in SUMMONER_TYPES: 
        self.end_attack_type = "SUMMS"
        self.chase_distance = SUM_ATTACK_DIST

    if self.end_attack_type == "MELEE" and self.xp_level <= LEVEL_UPGRADES[0]: 
        self.current_attack_type = "MID"
        self.chase_distance = MID_ATTACK_DIST
    elif self.end_attack_type == "LONG" and self.xp_level <= LEVEL_UPGRADES[0]: 
        self.current_attack_type = "MID"
        self.chase_distance = MID_ATTACK_DIST
    else: self.current_attack_type = self.end_attack_type

    self.fight_timer = 0
    self.running_away = False

    


###============== ON EVOLVE ==============###
"""
On evolve func gets called whenever the tank evolves and changes type. 
"""

def no_react(self):
    return False

def change_attack_type(self):
    if self.end_attack_type == "MELEE" and self.xp_level >= LEVEL_UPGRADES[0]:
        self.current_attack_type = "MELEE"
        self.chase_distance = 0
    elif self.end_attack_type == "LONG" and self.xp_level >= LEVEL_UPGRADES[0]:
        self.current_attack_type = "LONG"
        self.chase_distance = LONG_ATTACK_DIST



###============== EVOLUTION PATH ==============###
"""
Gets called when the tank first starts, and it chooses the evolution path that the tank will follow for the rest of the game. Gets called before the intro func and the upgrade levels func.
"""
def random_path(self,starting_from="Basic"):
    path = [starting_from]
    current_type = starting_from
    while current_type in TANK_UPGRADE_TREE:
        current_type = choice(TANK_UPGRADE_TREE[current_type])
        path.append(current_type)
    return path

###============== UPGRADE LEVELS ==============###
"""
Gets called when the tank first starts, chooses the upgrades it will take. Gets called after the evolution and intro funcs.
"""
def random_levels(self,evolution_path):
    level_upgrades = []
    for _ in range(MAX_LEVEL):
        try_upgrade = randrange(0,TANK_STATS_LEN)
        while level_upgrades.count(try_upgrade) >= MAX_STAT_LVL: try_upgrade = randrange(0,TANK_STATS_LEN)
        level_upgrades.append(try_upgrade)
    return level_upgrades

LEVEL_DISTRS = {
    #Max Health, Health Regeneration, Player Speed, Body Damage,    Bullet Damage, Bullet Endurance, Bullet Speed, Reload
    "MELEE" : [8,8,8,10, 1,1,1,1],
    "MID"   : [2,3,5,1, 7,7,6,4],
    "LONG"  : [2,1,3,1, 6,7,8,2],
    "SUMMS" : [2,1,2,1, 6,7,8,9]
}
def final_levels(self,evolution_path): #assumes type_check_init was already run to define self.end_attack_type
    inds = []
    for c,i in enumerate(LEVEL_DISTRS[self.end_attack_type]): inds += [c]*i

    level_upgrades = []
    for _ in range(MAX_LEVEL):
        try_upgrade = choice(inds)
        while level_upgrades.count(try_upgrade) >= MAX_STAT_LVL: try_upgrade = choice(inds)
        level_upgrades.append(try_upgrade)
    return level_upgrades




###============== UPDATE FUNCS ==============###
"""
Gets called every update of the bot, is given the ticks of the game.
Expected to use:
    -get_nearby(self) -> to find nearby entities. 
    
    -self.faceTowards(target_pos) -> to set facing direction
    -self.shoot() or self.auto_fire = True/False -> to set if the bot should shoot
    -self.accelerate(normalised_vec) -> to move the bot
"""

def attack_nearest_target(self, ticks): 
    """
    Basic agent - attacks nearest target, follows random upgrade path for stats and evolutions.
    """
    # Pick target
    if ticks % 30 == 0: #FIXME report when target dies and remove reference
        nearby_ents = get_nearby(self)
        if nearby_ents != []: self.target = min(nearby_ents, key = lambda x : coDistance(x.pos, self.pos))
        elif self.target.DRAW_CODE != DRW_NONE or coDistance(self.pos, self.target.pos) < self.chase_distance: self.target = DummyPosition(self.game.randomPos())

    # Look at target
    self.faceTowards(self.target.pos)

    # Navigate to/Shoot at target
    dist = coDistance(self.pos, self.target.pos)
    if dist <= self.chase_distance:
        self.auto_fire = True
        self.follower_move_code = 0 #attack/hover code
        if self.target.DRAW_CODE != DRW_NONE: self.follower_move_pos = self.target.pos
        else: self.follower_move_pos =  dA(self.pos, vecSub(dS(self.target.pos, self.pos), self.radius*4 + self.current_followers*0.5))
    else:
        self.follower_move_code = 0#attack/hover code
        self.follower_move_pos =  dA(self.pos, vecSub(dS(self.target.pos, self.pos), self.radius*4 + self.current_followers*0.5))
        self.auto_fire = False
        self.accelerate(vecSub(dS(self.target.pos,self.pos),1))


def guardian_attack_nearest_target(self, ticks): 
    """
    Basic agent - attacks nearest target, follows random upgrade path for stats and evolutions.
    """
    # Pick target
    if ticks % 30 == 0:
        nearby_ents = list(filter(lambda x: x != self and (x.DRAW_CODE in [DRW_FOOD, DRW_TANK_BOT, DRW_TANK_PLR]) and ( (not x.DRAW_CODE in TANK_CODES) or x.team == TEAM_NULL or x.team != self.team), self.game.chunkManager.getInRect(dA(self.pos, BOT_VIEW_RECT[:2]), dS(self.pos, BOT_VIEW_RECT[:2]))))
        if nearby_ents != []: self.target = min(nearby_ents, key = lambda x : coDistance(x.pos, self.pos))
        elif self.target.DRAW_CODE != DRW_NONE or coDistance(self.pos, self.target.pos) < self.chase_distance: self.target = DummyPosition(self.game.randomPos())

    # Look at target
    self.faceTowards(self.target.pos)

    # Navigate to/Shoot at target
    dist = coDistance(self.pos, self.target.pos)
    # if self.guardian: print(self.auto_fire, dist, dist <= self.chase_distance)
    if dist <= self.chase_distance:
        self.auto_fire = True
        self.follower_move_code = 0 #attack/hover code
        if self.target.DRAW_CODE != DRW_NONE: self.follower_move_pos = self.target.pos
        else: self.follower_move_pos =  dA(self.pos, vecSub(dS(self.target.pos, self.pos), self.radius*4 + self.current_followers*0.5))
    else:
        self.auto_fire = False

MAX_FIGHT_TIMER = FPS*30

def attack_type_risks(self, ticks):
    in_fight = False
    if ticks % 30 == 0:
        #FIXME make paths not go into food!
        self.running_away = False
        nearby_ents = get_nearby(self) 
        nearby_enemies = [col_obj for col_obj in nearby_ents if col_obj.DRAW_CODE in TANK_CODES]
        nearby_food = [col_obj for col_obj in nearby_ents if col_obj.DRAW_CODE == DRW_FOOD]
        in_danger = (self.current_attack_type == "MELEE" and self.health <= self.max_health/2) or (self.current_attack_type != "MELEE" and self.health <= self.max_health/5)
        # if in_danger and self.current_attack_type == "MELEE": print("danger!",self.health, self.max_health, self.name)
        if nearby_enemies != []:
            if any([t.xp_level >= self.xp_level+5 for t in nearby_enemies]) or in_danger or self.fight_timer >= MAX_FIGHT_TIMER: 
                scariest_t = max(nearby_enemies, key = lambda x : x.xp_level)
                away_vec = vecSub(dS(self.pos, scariest_t.pos),-1000)
                self.target = DummyPosition(dS(self.pos,away_vec)) #run away!
                self.running_away = True
                in_fight = True
            else: 
                self.target = self.target = min(nearby_enemies, key = lambda x : coDistance(x.pos, self.pos))
                in_fight = True

        elif nearby_food != [] and not (in_danger and self.current_attack_type == "MELEE"): self.target = min(nearby_food, key = lambda x : coDistance(x.pos, self.pos))

        elif self.target.DRAW_CODE != DRW_NONE or coDistance(self.pos, self.target.pos) < self.chase_distance+20: self.target = DummyPosition(self.game.randomPos())

    # Look at target
    if self.current_attack_type == "MELEE": self.faceTowards(self.target.pos,pi)
    else: self.faceTowards(self.target.pos)

    # Navigate to/Shoot at target
    dist = coDistance(self.pos, self.target.pos)
    if dist <= self.chase_distance:
        self.auto_fire = True
        self.follower_move_code = 0 #attack/hover code
        if self.target.DRAW_CODE != DRW_NONE: self.follower_move_pos = self.target.pos
        else: self.follower_move_pos =  dA(self.pos, vecSub(dS(self.target.pos, self.pos), self.radius*4 + self.current_followers*0.5))
    else:
        self.follower_move_code = 0#attack/hover code
        self.follower_move_pos =  dA(self.pos, vecSub(dS(self.target.pos, self.pos), self.radius*4 + self.current_followers*0.5))
        self.accelerate(vecSub(dS(self.target.pos,self.pos),1))
        if self.current_attack_type == "MELEE": #use gun to navigate as a melee tank
            self.auto_fire = True
        else:
            self.auto_fire = False

    if self.target.DRAW_CODE in TANK_CODES or self.running_away: in_fight = True

    if in_fight: self.fight_timer += 1
    else: self.fight_timer = 0




BOT_AI_FUNCS = { #intro func, on evolve func, choose upgrade levels, choose evolution path, update func
    "Basic Random"  : (basic_init, no_react, random_levels, random_path, attack_nearest_target),
    "Guardian"      : (basic_init, no_react, random_levels, random_path, guardian_attack_nearest_target),
    "Min Viable"    : (type_check_init, change_attack_type, final_levels, random_path, attack_type_risks)
}