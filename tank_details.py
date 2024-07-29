from math import pi
"""
Defines turret configuration.

"""
BULLET_TYPE_CODE = 0
FOLLOW_TYPE_CODE = 1

"""
TANKS TO ADD:
Necromancer: recruits dead food
Trapper: places mines
"""
#Stats - [Max Health, Health Regeneration, Player Speed, Body Domage,    Bullet Damage, Bullet Endurance, Bullet Speed, Reload ||    Tank Radius, Tank Shape Type, Min zoom]
TANK_STATS = { #max at 5
    "Basic"         : [0,0,0,0,     0,0,0,0,        10,0,2.5],

    "Flank"         : [1,0,0,0,     0,0,0,1,        10,0,2.5],
    "Sniper"        : [1,0,-1,0,    1,1,1,-1,       10,0,2.25],
    "Machine Gun"   : [1,0,0,0,     -1,0,0,1,       10,0,2.5],
    "Twin"          : [1,0,0,0,     0,0,0,1,        10,0,2.5],

    "Hybrid"        : [2,1,1,0,     1,0,0,2,        12,0,2.5],
    "Quad"          : [2,1,1,0,     0,0,1,2,        12,0,2.5],
    "Double Twin"   : [2,1,1,0,     1,0,0,2,        12,0,2.5],
    "Cannon"        : [2,1,1,1,     2,3,2,-3,       12,0,2.5],
    "Overseer"      : [2,1,1,0,     1,2,1,0,        12,0,2.5],
    "Hunter"        : [2,1,-1,0,    2,1,2,-1,       12,0,2],
    "Gunner"        : [2,1,1,0,     -1,-1,0,4,      10,0,2.5],
    "Triple Shot"   : [2,1,1,1,     1,0,0,2,        12,0,2.5],

    "Octo"          : [3,2,2,0,     0,0,2,3,        15,0,2.5],
    "Quad Twin"     : [3,2,2,0,     2,0,2,2,        15,0,2.5],
    "Battleship"    : [3,2,-3,0,    0,2,3,2,        15,0,2.5],
    "Auto Gunner"   : [3,2,2,0,     0,-1,2,2,       10,0,2.5],
    "Fighter"       : [0,2,2,0,     5,5,5,5,        15,0,2.5],
    "Penta Shot"    : [3,2,2,0,     2,0,0,3,        15,0,2.5],
    "Mortar"        : [3,2,2,0,     5,4,3,-5,       15,0,2.5],
    "Stalker"       : [3,2,0,0,     5,3,5,-1,       15,0,1.75],
    "Boxer"         : [5,3,4,5,     0,0,0,0,        20,0,2.5]
}


ALL_TANK_NAMES = list(TANK_STATS)
TANK_PREVIEW_ZOOM = {
    "Basic"         : 3,
    "Flank"         : 3,
    "Hybrid"        : 3,
    "Sniper"        : 2,
    "Machine Gun"   : 3,
    "Twin"          : 3,
    "Quad"          : 3,
    "Double Twin"   : 3,
    "Cannon"        : 3,
    "Overseer"      : 3,
    "Hunter"        : 2,
    "Gunner"        : 3,
    "Triple Shot"   : 3,
    "Octo"          : 3,
    "Quad Twin"     : 3,
    "Battleship"    : 3,
    "Auto Gunner"   : 3,
    "Fighter"       : 3,
    "Penta Shot"    : 3,
    "Mortar"        : 3,
    "Stalker"       : 2,
    "Boxer"         : 2
}

#orientation is 0:1
#Turret specs - {[bullet type code, turret width, turret length, orientation, perp_offset],...}
TANK_TURRET_SPECS = {
    "Basic"         : [ [BULLET_TYPE_CODE,5,17,0,0 ] ],
    "Flank"         : [ [BULLET_TYPE_CODE,5,17,0,0 ], [BULLET_TYPE_CODE,5,17,0.5,0 ]  ],
    "Hybrid"        : [ [BULLET_TYPE_CODE,6,23,0,0 ], [FOLLOW_TYPE_CODE,6,17,0.5,0 ] ],
    "Sniper"        : [ [BULLET_TYPE_CODE,6,28,0,0 ] ],
    "Machine Gun"   : [ [BULLET_TYPE_CODE,8,17,0,0 ] ],
    "Twin"          : [ [BULLET_TYPE_CODE,5,17,0,-3 ], [BULLET_TYPE_CODE,5,17,0,3 ] ],
    "Quad"          : [ [BULLET_TYPE_CODE,5,17,0,0 ], [BULLET_TYPE_CODE,5,17,0.25,0 ], [BULLET_TYPE_CODE,5,17,0.5,0 ], [BULLET_TYPE_CODE,5,17,0.75,0 ] ],
    "Double Twin"   : [ [BULLET_TYPE_CODE,5,17,0,-3 ], [BULLET_TYPE_CODE,5,17,0,3 ], [BULLET_TYPE_CODE,5,17,0.5,-3 ], [BULLET_TYPE_CODE,5,17,0.5,3 ] ],
    "Cannon"        : [ [BULLET_TYPE_CODE,10,19,0,0 ]  ],
    "Overseer"      : [ [FOLLOW_TYPE_CODE,7,16,0,0 ] ],
    "Hunter"        : [ [BULLET_TYPE_CODE,8,30,0,0 ] ],
    "Gunner"        : [ [BULLET_TYPE_CODE,4,13,-0.04,-2 ],[BULLET_TYPE_CODE,3,13,0.04,2 ], [BULLET_TYPE_CODE,3,15,0.04,0 ], [BULLET_TYPE_CODE,3,15,-0.04,0 ], [BULLET_TYPE_CODE,4,17,0,0 ] ],
    "Triple Shot"   : [ [BULLET_TYPE_CODE,6,23,0,0 ], [BULLET_TYPE_CODE,5,17,0.6,0 ], [BULLET_TYPE_CODE,5,17,-0.6,0 ] ],
    "Octo"          : [ [BULLET_TYPE_CODE,5,17,0,0 ], [BULLET_TYPE_CODE,5,17,0.125,0 ], [BULLET_TYPE_CODE,5,17,0.25,0 ], [BULLET_TYPE_CODE,5,17,0.375,0 ], [BULLET_TYPE_CODE,5,17,0.5,0 ], [BULLET_TYPE_CODE,5,17,0.625,0 ], [BULLET_TYPE_CODE,5,17,0.75,0 ], [BULLET_TYPE_CODE,5,17,0.875,0 ], ],
    "Quad Twin"     : [ [BULLET_TYPE_CODE,5,17,0,-3 ], [BULLET_TYPE_CODE,5,17,0,3 ], [BULLET_TYPE_CODE,5,17,0.25,-3 ], [BULLET_TYPE_CODE,5,17,0.25,3 ], [BULLET_TYPE_CODE,5,17,0.5,-3 ], [BULLET_TYPE_CODE,5,17,0.5,3 ], [BULLET_TYPE_CODE,5,17,0.75,-3 ], [BULLET_TYPE_CODE,5,17,0.75,3 ] ],
    "Battleship"    : [ [FOLLOW_TYPE_CODE,10,20,0.25,0 ], [FOLLOW_TYPE_CODE,10,20,0.75,0] ],
    "Auto Gunner"   : [ [BULLET_TYPE_CODE,4,15,-0.04,-2 ],[BULLET_TYPE_CODE,3,15,0.04,2 ], [BULLET_TYPE_CODE,3,17,0.04,-0.5 ], [BULLET_TYPE_CODE,3,17,-0.04,0.5 ], [BULLET_TYPE_CODE,4,19,0,0 ], [BULLET_TYPE_CODE,6,19,0.5,0] ],
    "Fighter"       : [ [BULLET_TYPE_CODE,7.5,17*1.5,0,0 ] ], 
    "Penta Shot"    : [ [BULLET_TYPE_CODE,6,23,0,0 ], [BULLET_TYPE_CODE,5,17,0.6,0 ], [BULLET_TYPE_CODE,5,17,-0.6,0 ], [BULLET_TYPE_CODE,5,17,0.8,0 ], [BULLET_TYPE_CODE,5,17,-0.8,0 ]  ],
    "Mortar"        : [ [BULLET_TYPE_CODE,18,20,0,0 ]  ],
    "Stalker"       : [ [BULLET_TYPE_CODE,8,32,0,0 ] ],
    "Boxer"         : [ ]
}



TANK_UPGRADE_TREE = {
"Basic"         : [ "Flank", "Sniper" , "Machine Gun" , "Twin" ],

"Flank"         : [ "Quad", "Double Twin", "Gunner"],
"Sniper"        : [ "Overseer", "Hunter" ],
"Machine Gun"   : ["Gunner", "Triple Shot", "Cannon"],
"Twin"          : ["Hybrid", "Triple Shot", "Double Twin"],

"Cannon"        : ["Mortar","Boxer"],
"Quad"          : ["Octo" ],
"Double Twin"   : ["Quad Twin" ] ,
"Overseer"      : ["Battleship" ] ,
"Hunter"        : ["Stalker" ] ,
"Gunner"        : ["Auto Gunner" ] ,
"Hybrid"        : ["Fighter" ] ,
"Triple Shot"   : ["Penta Shot" ],

}

MID_RANGER_TYPES = ["Basic", "Flank", "Machine Gun", "Twin", "Quad", "Double Twin", "Cannon" , "Gunner", "Triple Shot", "Octo", "Quad Twin", "Auto Gunner", "Fighter", "Penta Shot", "Mortar", ]
LONG_RANGER_TYPES = ["Sniper", "Hunter", "Stalker"]
SUMMONER_TYPES = ["Overseer", "Battleship", "Hybrid"]
MELEE_TYPES = ["Boxer"]
"""
Some useful math:

for some system
a (acceleration)
r (drag coeffiecent)
v (velocity)
vf (terminal velocity)

v = 0
loop:
    v = r*v + a

vf = a/(1-r)
(1-r)*vf = a
r = 1 - a/vf

or

v = 0
loop:
    v = r*(v + a)

vf = (r*a)/(1-r)
"""
