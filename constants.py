import math

MAP_CONSTANT = 3000
D_R_CONST = math.pi/180
# POLY_AREAS = [ polyArea(n+3,40) for n in range(3) ]



MAP_RECT = [-MAP_CONSTANT,-MAP_CONSTANT,MAP_CONSTANT*2,MAP_CONSTANT*2]
MAP_AREA = MAP_RECT[2]*MAP_RECT[3]

MAP_SPAWN_RECT = [-MAP_CONSTANT+20, -MAP_CONSTANT+20, MAP_CONSTANT*2-20*2, MAP_CONSTANT*2-20*2]

LEVEL_UPGRADES = [10, 20, 30]
MAX_LEVEL = 30

MAX_TANK_UPGRADE = 8
BULLET_HEALTH_M, BULLET_ENDURANCE_M, BULLET_SPEED_M, BULLET_DMG_M = 5,5,1,1

LEADERBOARD_LEN = 7

# adds = [ [n%2,n//2] for n in range(4) ]#
# adds2 = [ [n%5-2,n//5-2] for n in range(25) ]

KILL_XP_MULT = 0.4

CRCL_SH_CD = 0 #[radius]
POLY_SH_CD = 1 #[points centered at the origin]

DRW_NONE     = -1
DRW_TANK_PLR = 0
DRW_TANK_BOT = 1
DRW_FOOD     = 2
DRW_PROJ_BLT = 3
DRW_PROJ_FLW = 4



DRW_ORDER = [
    [DRW_PROJ_BLT, DRW_PROJ_FLW],
    [DRW_FOOD],
    [DRW_TANK_BOT, DRW_TANK_PLR]
]

FOOD_DENSITY = 25#how many food per 1,000,000 units^2 (1,000 units)^2
STATIC_FOOD_NUM = int(FOOD_DENSITY * MAP_AREA/(1000000))
# print("num foods",STATIC_FOOD_NUM)

CIRCLE_CODES = [DRW_PROJ_BLT,DRW_TANK_BOT,DRW_TANK_PLR]
POLY_CODES = [DRW_FOOD, DRW_PROJ_FLW]
TANK_CODES = [DRW_TANK_BOT, DRW_TANK_PLR]

SHP_TRIANGLE = 3
SHP_SQUARE = 4
SHP_PENTAGON = 5
SHP_LARGE_PENTAGON = 6

SHP_CODES = [SHP_TRIANGLE, SHP_SQUARE, SHP_PENTAGON, SHP_LARGE_PENTAGON]

SHP_SIDES   = [0,0,0,3,4,5,5]
SHP_SIZES   = [0,0,0,12,15,18,20] ##change size back when optimization is fixed, and change the chunk size
SHP_XP      = [0,0,0,20,10,100,10000]
SHP_HEALTH  = [0,0,0,10,30,250, 10000]

FOOD_HUB_BORDER = 100
FOOD_HUB_RECT = [-MAP_CONSTANT+FOOD_HUB_BORDER, -MAP_CONSTANT+FOOD_HUB_BORDER, MAP_CONSTANT*2-2*FOOD_HUB_BORDER, MAP_CONSTANT*2-2*FOOD_HUB_BORDER]
FOOD_HUB_DENSITY = 1 #how many hubs per 1,000,000 units^2 = (10,000 units)^2
FOOD_HUB_N = int(FOOD_HUB_DENSITY * MAP_AREA/(1000000))
# print("FOOD HUBS:",FOOD_HUB_N)
### Set up food spawning map

FOOD_HUB_CHANCE    = 80 #out of 100

FOOD_HUB_SEPERATION = 100
FOOD_SPAWN_WEIGHT  = [3]*(10) + [4]*8 + [5]*1
FOOD_HUB_CODES     = [[3],  [4],    [3,3,3,4],  [5],     [3,4,4,5],      [5]*30+[6]*1] 
FOOD_HUB_RADII     = [200,  150,    250,        150,     350,            400] 
FOOD_HUB_FREQ      = [4,    4,      8,          2,        6,            1]
FOOD_HUB_W_INDS    = []
for n in range(len(FOOD_HUB_CODES)): FOOD_HUB_W_INDS += [n]*FOOD_HUB_FREQ[n]

COL_TOLERANCE = 150

WEIGHTED_FOOD_CODES = [5]*1 + [3]*4 + [4]*5


FOOD_VEL_TOLERANCE = 0.02
FOOD_ROT_VEL_TOLERANCE = 0.005

BOT_ROT_DRAG = 0.6
BOT_ROT_VEL_TOLERANCE = 0.001
BOT_ROT_TOLERANCE = 0.02
BOT_ROT_ACC_MAG = 0.08
BOT_ROT_ACC_LIMITER = 0.08

DRAG = 0.95
BULLET_DRAG = 0.98
FOLLOWER_DRAG = 0.95
ROT_DRAG = 0.80
FOOD_ROT_DRAG = 0.99
FOOD_DRAG = 0.99

FOOD_ROT_COEFF = 0.5
MAX_FOOD_ROT_VEL = 0.2


ROT_TOLERANCE = 0.001
PROJ_MOM_TRANSFER = 0.3

FLW_SIZE_MULT = 3
FLW_ACC_MULT = 0.04
FLW_DIST = 5
FLW_DIST_MULT = 0.2
FLW_DEFLECT_MULT = 0.3
FLW_ROT_ACC_MAG = 0.02
FLW_ROT_ACC_LIMITER = 0.02

DNSTY_TANK = 10
DNSTY_BULLET = 4
DNSTY_FLWR = 1
DNSTY_TRT = 10
DNSTY_FOOD = 5

LENGTH_DRAW_TICKS_HALF = 10
LENGTH_DRAW_SCALE = 1

CHUNK_SIZE = 40
NEIGHBOURS = [(-1,-1), (0,-1), (1,-1), (-1,0),(0,0), (1,0), (-1,1), (0,1), (1,1)] #includes self

SHOW_FPS = True

DMG_ANIMATION_DURATION = 20

HB_WIDTH = 15
HB_HEIGHT = 3

TRI_COEFF = math.sqrt(3)/4

TANK_STATS_NAMES = ["Max Health", "Health Regeneration", "Player Speed", "Body Damage", "Bullet Damage", "Bullet Endurance", "Bullet Speed", "Reload"]
TANK_STATS_LEN = len(TANK_STATS_NAMES)

PLAYER_EVOLVE_SQUARES = [[10+x*160,10+y*160,150,150] for x,y in [(0,0),(0,1),(1,0),(1,1)]]
PREVIEW_ROT_SPEED = 0.02

ZOOM_STRENGTH = 1.05
ZOOM_RANGE = [2,6.5]


STATIC_BOTS_NUM = 20

NAME_TEXT_SIZE_MULT = 0.5

PLAYER_NAME = "Cragon"

MAX_STAT_LVL = 8

TEAM_NULL = -1
TEAM_0 = 0
TEAM_1 = 1
TEAM_2 = 2
TEAM_3 = 3

EXTRA_OPTION_TEXT = ["", "", " Teams"]

BOT_VIEW_DIST = [1024, 576] #rectangular because human view is rectangular
BOT_VIEW_RECT = [-BOT_VIEW_DIST[0]//2, -BOT_VIEW_DIST[1]//2] + BOT_VIEW_DIST

SPAWN_FIELD_WIDTH = 600

GUARDIAN_FIRE_DIST = 200*(2**0.5)
GUARDIAN_OFFSET = 1200
GUARDIAN_AREA_WIDTH = 400
GUARDIAN_NEUTRAL_COL = [200,200,200]

GRID_SIZE = 200


SOUND_SETTING_NAMES = ["Global", "Music", "SFX"]
SOUND_SLIDER_RADIUS = 10

FPS = 60


MAX_AREA_TICKS = FPS*300