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

###============== INTRO ==============###
def basic_init(self,tank_type=None):
    self.auto_fire = False
    self.follow_move_code = 0



###============== EVOLUTION PATH ==============###
def random_path(starting_from="Basic"):
    path = [starting_from]
    current_type = starting_from
    while current_type in TANK_UPGRADE_TREE:
        current_type = choice(TANK_UPGRADE_TREE[current_type])
        path.append(current_type)
    return path

###============== UPGRADE LEVELS ==============###
def random_levels(evolution_path):
    level_upgrades = []
    for _ in range(MAX_LEVEL):
        try_upgrade = randrange(0,TANK_STATS_LEN)
        while level_upgrades.count(try_upgrade) > MAX_STAT_LVL: try_upgrade = randrange(0,TANK_STATS_LEN)
        level_upgrades.append(try_upgrade)
    return level_upgrades



###============== UPDATE FUNCS ==============###

def attack_nearest_target(self, ticks): 
    """
    Basic agent - attacks nearest target, follows random upgrade path for stats and evolutions.
    """
    # Pick target
    if ticks % 30 == 0: #FIXME report when target dies and remove reference
        nearby_ents = list(filter(lambda x: x != self and (x.DRAW_CODE in [DRW_FOOD, DRW_TANK_BOT, DRW_TANK_PLR]) and ( (not x.DRAW_CODE in TANK_CODES) or x.team == TEAM_NULL or x.team != self.team), self.game.chunkManager.getInRect(dA(self.pos, BOT_VIEW_RECT[:2]), dS(self.pos, BOT_VIEW_RECT[:2]))))
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

    #if randrange(0,50) == 0: self.addXP(1000) #FIXME remove
    
    # Check for level ups
    while (self.upgrade_points > 0):
        stat_ind = randrange(0,TANK_STATS_LEN)
        while self.tank_stats[stat_ind] >= MAX_STAT_LVL: stat_ind = randrange(0,TANK_STATS_LEN)
        self.upgradeStat(stat_ind)
    while self.evolve_upgrade_points > 0:
        if self.tank_type in TANK_UPGRADE_TREE: 
            self.changeTankType(choice(TANK_UPGRADE_TREE[self.tank_type]))
            self.evolve_upgrade_points -= 1






BOT_AI_FUNCS = { #intro func, choose upgrade levels, choose evolution path, update func
    "Basic Random" : (basic_init, random_levels, random_path, attack_nearest_target)
}