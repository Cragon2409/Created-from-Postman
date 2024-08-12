"""
Made by Samuel Price, not intended for commercial distribution.
"""

##################################################################
###                          IMPORTS                           ###
##################################################################

import pygame,math
from random import randrange,choice
from helpers import *
from tank_details import *
from constants import *
from bots_ai import *


##################################################################
###                          SETUP                             ###
##################################################################
pygame.init()

screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
dw,dh = pygame.display.get_surface().get_size()
dim = [dw,dh]

display_width, display_height = dw,dh
pygame.display.set_caption("Pygame")
clock = pygame.time.Clock()

pygame.font.init()
myfont = pygame.font.SysFont("monospace", 20)
fancyFont = pygame.font.SysFont("calibri", 22)
big_font = pygame.font.SysFont("calibri", 80)

##################################################################
###                          GRAPHICS CONSTANTS                ###
##################################################################

S_CENT = [dw//2, dh//2]
S_RECT = [0,0,dw,dh]
EX_MARGIN = 300

EX_S_RECT = [-EX_MARGIN, -EX_MARGIN, dw+2*EX_MARGIN, dh+2*EX_MARGIN]
S_CORNER_POS = [[0,0], [dw,0], [dw,dh], [0,dh]]
M_DI = {pygame.K_w:(0,-1),pygame.K_a:(-1,0),pygame.K_s:(0,1),pygame.K_d:(1,0)}

BORDER_COLOUR = [200]*3
XPB_LENGTH = (dw-120)//5
XPB_POS = dw//2-XPB_LENGTH//2

SHP_COLS = [None,None,None, red, yellow, blue, purple]

MESSAGE_LOG_POS = [dw-400,dh-50]
LEADERBOARD_POS = [dw-350,450]

PLAYER_STATS_RECTS = [[10,dh-TANK_STATS_LEN*32+n*32,205,30] for n in range(TANK_STATS_LEN)]
PLAYER_STATS_POINTS_POS = dA(PLAYER_STATS_RECTS[0], [3,-30])

MINIMAP_POS = [dw-120, 50]

HORIZON_LINE = dh//2
VER_SKY_COL = [10,5,5]
VER_LAND_COL = [180]*3
VER_LINE_COL = darkgreen

##################################################################
###                          GLOBAL VARS                       ###
##################################################################

TANKS = {}

##################################################################
###                     GRAPHICS SETUP/HELPERS                 ###
##################################################################

def simpleText(inputText,co=(0,0),colour=white,font = fancyFont):
    text = font.render(inputText, True, colour)
    screen.blit(text,co)
def messageDisplay(text,colour=white,center = [dw/2,dh/2]):
    TextSurf, TextRect = textObjects(text,fancyFont,colour)
    TextRect.center = center
    screen.blit(TextSurf, TextRect)
def dynamicMessageDisplay(text,colour=white,size=50,center = [dw/2,dh/2], font_name = "calibri"):
    font = pygame.font.SysFont(font_name, size)
    TextSurf, TextRect = textObjects(text,font,colour)
    TextRect.center = center
    screen.blit(TextSurf, TextRect)

def borderedRect(pos,width,height,borderThickness,mainColour,borderColour):#pos is top left
    pygame.draw.rect(screen,borderColour,(pos[0],pos[1],width,height))
    tBT = borderThickness*2
    pygame.draw.rect(screen,mainColour,(pos[0]+borderThickness,pos[1]+borderThickness,width-tBT,height-tBT))
def healthBar(pos,width,height,borderThickness,barColour,borderColour,backColour,percent):
    borderedRect(pos,width,height,borderThickness,backColour,borderColour)
    if percent != 0: pygame.draw.rect(screen,barColour,list(dA(pos,(borderThickness,borderThickness))) + [min(100,max(0,(percent)))*(width-borderThickness*2),height-borderThickness*2])
def centText(inputText,center,colour=white,font=fancyFont):
    textSurf, textRect = textObjects(inputText,font,colour)
    textRect.center = center
    screen.blit(textSurf,textRect)

PDU = pygame.display.update

##################################################################
###                   CLASS DEFINITIONS                        ###
##################################################################

### Collision Handling and Optimisations
class ChunkManager:
    def __init__(self):
        self.chunk_dict = dict()
    def add(self, col_obj): 
        chunk_st = self.posToChunk(col_obj.pos)
        col_obj.chunk_st = chunk_st
        if not chunk_st in self.chunk_dict: self.chunk_dict[chunk_st] = [col_obj] 
        else: self.chunk_dict[chunk_st].append(col_obj)
    def update_obj(self, col_obj):
        new_chunk_st = self.posToChunk(col_obj.pos)
        if new_chunk_st != col_obj.chunk_st:
            self.chunk_dict[col_obj.chunk_st].remove(col_obj) #remove old chunk entity
            if self.chunk_dict[col_obj.chunk_st] == []: del self.chunk_dict[col_obj.chunk_st]

            col_obj.chunk_st = new_chunk_st #add new chunk entity
            if not new_chunk_st in self.chunk_dict: self.chunk_dict[new_chunk_st] = [col_obj]
            else: self.chunk_dict[new_chunk_st].append(col_obj)
    def remove(self, col_obj):
        try:
            self.chunk_dict[col_obj.chunk_st].remove(col_obj) #remove old chunk entity
            if self.chunk_dict[col_obj.chunk_st] == []: del self.chunk_dict[col_obj.chunk_st]
        except:
            print("error found!",col_obj)
            print(col_obj.owner)
            1/0
    def posToChunk(self, pos):
        return str(int(pos[0]//CHUNK_SIZE)) + '_' + str(int(pos[1]//CHUNK_SIZE))
    def posToChunkNum(self, pos):
        return [int(pos[0]//CHUNK_SIZE), int(pos[1]//CHUNK_SIZE)]
    def neighbouringChunks(self, chunk_st):
        ch_nums = [int(i) for i in chunk_st.split('_')]
        return ['_'.join([str(i) for i in dA(ch_nums,ne)]) for ne in NEIGHBOURS]
    def getChunk(self, chunk_st):
        if chunk_st in self.chunk_dict: return self.chunk_dict[chunk_st]
        else: return []
    def showDict(self):
        for k in self.chunk_dict:
            print(k, self.chunk_dict[k])
    def runCollisions(self): #assumes objects have been updated before running
        toKill = []
        for k in self.chunk_dict:
            for col_obj in self.chunk_dict[k]:
                if col_obj.checkCollisions(): toKill.append(col_obj)
        for col_obj in toKill[::-1]:
            col_obj.kill()
    def getInRect(self, top_left, bottom_right):
        entities = []
        top_left_chunk_nums = self.posToChunkNum(top_left)
        bottom_right_chunk_nums = self.posToChunkNum(bottom_right)
        for x_ch in range(top_left_chunk_nums[0]-1, bottom_right_chunk_nums[0]+2):
            for y_ch in range(top_left_chunk_nums[1]-1, bottom_right_chunk_nums[1]+2):
                chunk_st = str(x_ch) + '_' + str(y_ch)
                entities += self.getChunk(chunk_st)
        return entities
         

class CollisionObject:
    #vars: mass, density, pos, vel, DRAW_CODE
    #methods: hitBy, kill
    def __init__(self, game):
        self.game = game
        self.game.chunkManager.add(self)
    def colKill(self):
        self.game.chunkManager.remove(self)
    def getNearbyEntities(self):
        #assumes chunk string is updated
        nearby = []
        for chunk_st in self.game.chunkManager.neighbouringChunks(self.chunk_st): nearby += self.game.chunkManager.getChunk(chunk_st)
        nearby.remove(self)
        return nearby
    def checkCollisions(self):
        for col_obj in self.getNearbyEntities():
            if (not (self.DRAW_CODE == DRW_PROJ_BLT and col_obj.DRAW_CODE == DRW_PROJ_BLT and self.owner == col_obj.owner)) and ([col_obj.DRAW_CODE, self.DRAW_CODE] == [DRW_PROJ_FLW, DRW_PROJ_FLW] or TEAM_NULL in [self.team, col_obj.team] or self.team != col_obj.team) and self.collide(col_obj):
                if self.hitBy(col_obj): return True
        return False
    def collide(self, col_obj):
        if self.DRAW_CODE in POLY_CODES:
            if col_obj.DRAW_CODE in POLY_CODES: #polygon to polygon
                return (coDistance(self.pos,col_obj.pos) <= self.r + col_obj.r) and (pointInPoly(self.pos, col_obj.col_poly, col_obj.pos, col_obj.col_r, col_obj.col_rads) or any([pointInPoly(co,col_obj.col_poly, col_obj.pos, col_obj.col_r, col_obj.col_rads) for co in self.poly]) or any([pointInPoly(co,self.col_poly, self.pos, self.col_r, self.col_rads ) for co in col_obj.poly]))
            elif col_obj.DRAW_CODE in CIRCLE_CODES: #polygon to circle
                return (coDistance(self.pos, col_obj.pos) <= self.r + col_obj.radius) and (circleInPoly(col_obj.pos,col_obj.radius, self.poly, self.col_poly, self.pos, self.col_r, self.col_rads))
                # return (coDistance(self.pos, col_obj.pos) <= self.r + col_obj.radius) 
        elif self.DRAW_CODE in CIRCLE_CODES: 
            if col_obj.DRAW_CODE in POLY_CODES: #circle to polygon
                return (coDistance(col_obj.pos, self.pos) <= col_obj.r + self.radius) and (circleInPoly(self.pos,self.radius, col_obj.poly, col_obj.col_poly, col_obj.pos, col_obj.col_r, col_obj.col_rads))
            elif col_obj.DRAW_CODE in CIRCLE_CODES: #circle to circle
                return coDistance(self.pos, col_obj.pos) <= self.radius + col_obj.radius


### Weapon Systems
class Turret:
    density = DNSTY_TRT
    def __init__(self,game, parent_tank, bullet_type_code, width, length, orientation, perp_offset):
        self.game, self.bullet_type_code, self.width, self.length, self.orientation, self.perp_offset = game, bullet_type_code, width, length, orientation, perp_offset
        self.proj_type = PROJECTILE_TYPES[self.bullet_type_code]
        self.parent_tank = parent_tank
        self.mass = width*length*self.density

        self.base_length = length
        self.length_ticks = 0
    def shoot(self):
        if (self.proj_type == Bullet) or ( self.proj_type == Follower and self.parent_tank.current_followers <= self.parent_tank.max_followers):
            vec = vecRot(ciS(1,self.parent_tank.orientation),self.orientation)
            
            new_proj = self.proj_type(dA(self.parent_tank.vel,(dSM(self.parent_tank.bullet_speed, vec))), dA(self.parent_tank.pos,dA(dSM(self.length, vec),dSM(self.perp_offset, vecRotLeft(vec)))),self.width/2,self.parent_tank)
            self.parent_tank.projs.add(new_proj)

            bullet_force = self.parent_tank.bullet_speed*new_proj.mass
            acc = dSM(-bullet_force/self.parent_tank.mass,vec)
            self.length_ticks = LENGTH_DRAW_TICKS_HALF*2
            return True, acc
        return False, [0,0]
    def update(self):
        #FIXME move cooldown to each turret
        self.length_ticks = max(0,self.length_ticks-1)
        if self.length_ticks == 0: self.length = self.base_length
        elif self.length_ticks > LENGTH_DRAW_TICKS_HALF: self.length = self.base_length + LENGTH_DRAW_SCALE*(2*LENGTH_DRAW_TICKS_HALF - self.length_ticks)/LENGTH_DRAW_TICKS_HALF
        else: self.length = self.base_length + LENGTH_DRAW_SCALE*self.length_ticks/LENGTH_DRAW_TICKS_HALF


class Projectile(CollisionObject):
    def __init__(self,start_vel,start_pos,size,owner):
        self.owner = owner
        self.team = self.owner.team
        self.vel = start_vel 
        self.pos = start_pos
        self.health = owner.bullet_endur
        self.col_dmg = owner.bullet_damage
        super().__init__(owner.game)
    def kill(self):
        self.owner.killProj(self)
    def hitBy(self,col_obj):
        if (col_obj.DRAW_CODE in [DRW_TANK_PLR, DRW_TANK_BOT] and  col_obj == self.owner): return False
        elif (col_obj.DRAW_CODE in [DRW_PROJ_BLT,DRW_PROJ_FLW] and col_obj.owner == self.owner):
            if self.DRAW_CODE == DRW_PROJ_FLW and col_obj.DRAW_CODE == DRW_PROJ_FLW:
                vec_btwn = vecRot(vecSub(dS(self.pos, col_obj.pos),1), randrange(-10,11)/50)
                acc = dSM(FLW_DEFLECT_MULT*col_obj.mass/self.mass,vec_btwn)
                self.vel = dA(self.vel, acc)
            return False
        else:
            self.health = max(0, self.health - col_obj.col_dmg)
            if self.health == 0:
                if col_obj.DRAW_CODE in [DRW_TANK_PLR, DRW_TANK_BOT]:
                    col_obj.vel = dA(col_obj.vel, dSM(self.mass/col_obj.mass*PROJ_MOM_TRANSFER,self.vel))
                elif self.DRAW_CODE == DRW_PROJ_BLT and col_obj.DRAW_CODE in [DRW_FOOD,DRW_PROJ_FLW]: #FIXME implement surface normals instead of approximating with circles
                    #FIXME check math and maybe use projection, switch to language of normal surface vectors
                    intercept_dir = vecSub(dS(col_obj.pos,self.pos),1)
                    vel_unit = vecSub(self.vel, 1)
                    dot = vecDot(intercept_dir, vel_unit)

                    clockwise_t_rads = vecAngle(vecRotLeft(intercept_dir))
                    anticlockwise_t_rads = vecAngle(vecRotRight(intercept_dir))
                    vel_rads = vecAngle(vel_unit)
                    is_clockwise = closestRads(vel_rads,anticlockwise_t_rads,clockwise_t_rads)
                    rot_dir = (1 if is_clockwise else -1) #1 really should be clockwise not -1, but something is mixed up here
                    #positive is clockwise, negative is anticlockwise

                    factor_rot = -(1 - abs(dot)) * rot_dir
                    factor_push = abs(dot)
                    force = vecMag(self.vel) * self.mass
                    col_obj.vel = dA(col_obj.vel, dSM(force*factor_push/col_obj.mass*PROJ_MOM_TRANSFER,intercept_dir))
                    col_obj.rot_vel += FOOD_ROT_COEFF*force*factor_rot/col_obj.mOI
                return True

class Bullet(Projectile):
    DRAW_CODE = DRW_PROJ_BLT
    drag = BULLET_DRAG
    density = DNSTY_BULLET
    def __init__(self,start_vel,start_pos,size,owner):
        super().__init__(start_vel,start_pos,size,owner)
        self.radius = size
        self.mass = PI*self.radius**2*self.density
    def update(self):
        self.pos = dA(self.pos,self.vel)
        self.vel = dSM(self.drag, self.vel)
        self.game.chunkManager.update_obj(self)
        return vecMag(self.vel) < 0.1 or self.health == 0 #return true to kill
    
class Follower(Projectile):
    DRAW_CODE = DRW_PROJ_FLW
    drag = FOLLOWER_DRAG
    density = DNSTY_FLWR
    sides = 3
    col = [210,40,170]
    def __init__(self,start_vel,start_pos,size,owner):
        super().__init__(start_vel,start_pos,size,owner)
        self.side_length = size*FLW_SIZE_MULT
        self.mass = self.density * (TRI_COEFF) * self.side_length**2
        self.rotation = 0 #[0,1] range
        self.rot_vel = 0
        self.pos_anchor = self.pos[:]
        self.o_poly, self.r, self.o_col_poly, self.col_r, self.o_col_rads = generatePolygon([0,0], self.side_length, self.sides, 270/self.sides)
        self.updatePolys()
        self.poly = self.o_poly[:]
        self.col_poly = self.o_col_poly[:]
        self.col_rads = self.o_col_rads

        self.dmg_ticks = 0
        self.acc_mag = self.owner.bullet_speed*FLW_ACC_MULT
        
        self.mOI = self.mass * self.r**2 / 24 * (1 + 3*cot2(PI/self.sides))
    def updatePolys(self):
        shift = self.pos[:]
        self.col_rads = self.o_col_rads + self.rotation*2*PI  #FIXME check if the hitboxes still work
        self.poly = [dA(shift,vecRot(co,self.rotation)) for co in self.o_poly]
        self.col_poly = [dA(shift,vecRot(co,self.rotation)) for co in self.o_col_poly]
    def update(self):
        target_pos, attraction_mode = self.owner.getFollowerInfo()
        
        if attraction_mode == 0: #attraction
            dist = coDistance(self.pos, target_pos)
            if dist >= FLW_DIST + self.owner.current_followers*FLW_DIST_MULT: self.vel = dA(self.vel, vecSub(dS(target_pos,self.pos), self.acc_mag))
            else: pass#self.vel = dA(self.vel, [randrange(-50,51)/100 for _ in range(2)])

        elif attraction_mode == 1: #respulsion
            self.vel = dA(self.vel, vecSub(dS(target_pos,self.pos), -self.acc_mag))

        self.vel = dSM(self.drag, self.vel)
        self.pos = dA(self.pos,self.vel)

        self.faceDir(self.vel)
        self.rotation += self.rot_vel
        self.rot_vel *= ROT_DRAG
        self.updatePolys()

        self.game.chunkManager.update_obj(self)
        return self.health == 0 #return true to kill
    def faceDir(self,vec):
        t = vecAngle(vec)/(2*PI)
        p = self.rotation
        right_rot = (t-p)%1
        left_rot = (p-t)%1
        if abs(right_rot) < ROT_TOLERANCE or abs(left_rot) < ROT_TOLERANCE:  self.rot_vel *= ROT_DRAG
        elif right_rot > left_rot: self.rot_vel -= min([FLW_ROT_ACC_MAG,FLW_ROT_ACC_LIMITER*right_rot,FLW_ROT_ACC_LIMITER*left_rot])
        else: self.rot_vel += min([FLW_ROT_ACC_MAG,FLW_ROT_ACC_LIMITER*right_rot,FLW_ROT_ACC_LIMITER*left_rot])

        self.rotation = self.rotation % 1

PROJECTILE_TYPES = [Bullet, Follower] #TODO add mine type projectiles


### Tank Setup
class Tank(CollisionObject):
    density = DNSTY_TANK
    def __init__(self, game, start_pos, start_type="Basic"):
        self.tank_type = start_type
        self.game = game
        self.tank_stats = [0]*8
        self.xp_level = 0
        self.xp_points = 0
        self.xp_points_total = 0
        self.setMaxXP()
        self.upgrade_points = 0
        self.evolve_upgrade_points = 0
        self.max_health = self.health = 0 #set so starting health is correct
        self.assignStats()
        self.cooldown_timer = 0
        self.current_followers = 0
        self.health = self.max_health
        self.regen_timer = self.regen_ticks
        self.auto_fire = False
        self.projs = set()
        self.turrets = []
        for tur_stats in TANK_TURRET_SPECS[start_type]:
           self.turrets.append(Turret(self.game, self, *tur_stats))
        self.mass = PI*self.radius**2 + sum([tur.mass for tur in self.turrets])
        
        self.pos = start_pos
        self.orientation = 0
        self.ori_vel = 0
        self.vel = [0,0]
        super().__init__(game)
    def shoot(self):
        total_acc = [0,0]
        if self.cooldown_timer == 0:
            self.cooldown_timer = self.reload_ticks
            for tur in self.turrets:
                shot, acc = tur.shoot()
                if shot and tur.proj_type == Follower:
                    self.current_followers += 1
                total_acc = dA(total_acc, acc)
        self.vel = dA(self.vel, total_acc)
    def killProj(self,proj):
        if proj.DRAW_CODE == DRW_PROJ_FLW: self.current_followers -= 1
        proj.colKill()
        self.projs.remove(proj)
        del proj
    def setMaxXP(self):
        self.xp_points_needed = 30+self.xp_level*100
    def changeTankType(self,new_type):
        self.tank_type = new_type
        self.turrets = []
        for tur_stats in TANK_TURRET_SPECS[new_type]:
           self.turrets.append(Turret(self.game, self, *tur_stats))
        self.mass = PI*self.radius**2 + sum([tur.mass for tur in self.turrets])
        self.assignStats()
    def assignStats(self):
        stats = nupleAdd(TANK_STATS[self.tank_type], self.tank_stats + [0,0,0], 11)
        prev_max_health = self.max_health
        self.max_health = 100 + 10*stats[0]
        self.health += self.max_health - prev_max_health 

        #total stats get up to 15, tank stats max at 5 and player stats max at 10
        self.regen_ticks    = (600 - 30*stats[1])//20
        self.move_speed     = (1 + stats[2]/5)*0.1
        self.col_dmg        = 1 + stats[3]/2
        self.bullet_damage  = 1 + stats[4]
        self.bullet_endur   = 1 + stats[5]*0.5
        self.bullet_speed   = 2 + stats[6]/4
        self.reload_ticks   = 60 - stats[7]*4
        self.max_followers = 10 + stats[7]*2

        self.radius = stats[8]
        self.tank_shape_type = stats[9]
        if self.DRAW_CODE == DRW_TANK_PLR: 
            ZOOM_RANGE[0] = stats[10]
            self.game.camera.zoom = limit(self.game.camera.zoom, ZOOM_RANGE[1], ZOOM_RANGE[0])
    def accelerate(self,di): #assumes normalised direction
        self.vel = dA(self.vel,dSM(self.move_speed,di))
    def hitBy(self,col_obj):
        if not (col_obj.DRAW_CODE in [DRW_PROJ_BLT,DRW_PROJ_FLW] and col_obj in self.projs):
            self.health = max(0, self.health - col_obj.col_dmg)
            self.regen_timer = self.regen_ticks*20 #disable in combat regeneration (when hit)
            if self.health == 0:
                if col_obj.DRAW_CODE in [DRW_PROJ_BLT, DRW_PROJ_FLW]: killed_name = col_obj.owner.name
                else: killed_name = col_obj.name
                self.game.addMessage(self.name + " killed by " + killed_name, self.col, 360)
                if col_obj.DRAW_CODE in [DRW_TANK_BOT, DRW_TANK_PLR]: col_obj.reportKilled(self)
                elif col_obj.DRAW_CODE in [DRW_PROJ_BLT, DRW_PROJ_FLW]: col_obj.owner.reportKilled(self)
                return True
        return False
    def reportKilled(self,col_obj):
        if col_obj.DRAW_CODE == DRW_FOOD: self.addXP(SHP_XP[col_obj.sides])
        elif col_obj.DRAW_CODE in [DRW_TANK_BOT,DRW_TANK_PLR]: 
            self.addXP(col_obj.xp_points_total*KILL_XP_MULT)
    def addXP(self, xp_amount):
        self.xp_points += xp_amount
        self.xp_points_total += xp_amount
        while self.xp_points >= self.xp_points_needed and self.xp_level < MAX_LEVEL:
            self.xp_points -= self.xp_points_needed
            self.setMaxXP()
            self.xp_level += 1
            self.upgrade_points += 1
            if self.xp_level in LEVEL_UPGRADES:
                self.evolve_upgrade_points += 1  
            if self.DRAW_CODE == DRW_TANK_BOT: self.checkUpgrades()
    def update(self):
        #update position
        for n in range(2):
            nPos = self.pos[:]
            nPos[n] += self.vel[n]
            if not circleInRect(nPos,MAP_RECT,self.radius): self.vel[n] = 0
        self.vel = dSM(DRAG, self.vel)
        self.pos = dA(self.pos,self.vel)
        self.game.chunkManager.update_obj(self)

        #update firing 
        for tur in self.turrets: tur.update()
        self.cooldown_timer = max(0,self.cooldown_timer-1)
        if self.cooldown_timer == 0 and self.auto_fire: self.shoot()
        for proj in [proj for proj in self.projs if proj.update()][::-1]: self.killProj(proj)
            
        #update health regen
        self.regen_timer -= 1
        if self.regen_timer == 0:
            self.regen_timer = self.regen_ticks
            self.health = min(self.health+1,self.max_health)

        #update rot for bots
        self.orientation += self.ori_vel
        self.ori_vel *= BOT_ROT_DRAG
        if self.ori_vel < BOT_ROT_VEL_TOLERANCE: self.ori_vel = 0

        
        return False #dont delete bots!
    

class Player(Tank):
    DRAW_CODE = DRW_TANK_PLR
    name = PLAYER_NAME
    def __init__(self, game, camera, start_pos, start_type, team=TEAM_NULL, preview=False):
        self.preview = preview
        self.team = team
        self.col = PLAYER_COL if team == TEAM_NULL else TEAM_COLOURS[team]
        self.camera = camera
        self.camera.user = self
        self.dead = False
        if not preview: 
            super().__init__(game, start_pos, start_type)
        else: #preview initialisation
            self.game, self.pos, self.tank_type = game, start_pos, start_type
            self.vel = [0,0]
            self.turrets = []
            self.orientation = 0
            self.max_health = self.health = 0
            self.tank_stats = [0]*8
            self.assignStats()
            for tur_stats in TANK_TURRET_SPECS[start_type]: self.turrets.append(Turret(game, self, *tur_stats))
        self.game.user = self
    def onClick(self,m_co):
        if not self.auto_fire:
            self.shoot()
    def onPress(self,key):
        if key == pygame.K_e: self.auto_fire = not self.auto_fire
    def onPressed(self,keys):
        di = [0,0]
        for key in M_DI:
            if keys[key]: di = dA(di, M_DI[key])
        if di != [0,0]: self.accelerate(vecSub(di))
    def kill(self):
        self.dead = True
    def isDead(self):
        return self.dead
    def getFollowerInfo(self): #returns attraction pos, and attractor/repulse mode (0/1)
        m_r_pos = self.game.camera.dToR(pygame.mouse.get_pos())
        if pygame.mouse.get_pressed()[2]: #repulsor mode
            return m_r_pos, 1
        elif pygame.mouse.get_pressed()[0]: #follow mode
            return m_r_pos, 0
        else: #hover mode
            return dA(self.pos, vecSub(dS(m_r_pos, self.pos), self.radius*4 + self.current_followers*0.5)), 0
    def faceTowards(self,r_co):
        self.orientation = twoCoAngle(self.pos, r_co)   

class Bot(Tank):
    DRAW_CODE = DRW_TANK_BOT
    preview = False
    chase_distance = 100
    def __init__(self, game, start_pos, start_type, team=TEAM_NULL):
        super().__init__(game, start_pos, start_type)
        self.name = genUsername()  
        self.col = BOT_COL if team == TEAM_NULL else TEAM_COLOURS[team]
        self.team = team
        self.target = DummyPosition(self.game.randomPos())
        self.follower_move_code = 0
        self.follower_move_pos = self.pos
        self.intro_func, self.upgrade_levels_func, self.evolve_path_func, self.update_func = BOT_AI_FUNCS["Basic Random"]
        self.ori_vel = 0

        # Initialise AI
        self.intro_func(self,start_type)
        self.evolve_path = self.evolve_path_func()
        self.upgrade_point_path = self.upgrade_levels_func(self.evolve_path)
    def kill(self):
        self.game.killBot(self)  
    def getFollowerInfo(self):
        return self.follower_move_pos, self.follower_move_code
    def controlAI(self,ticks):
        self.update_func(self, ticks)
    #Agent Funcs
    def checkUpgrades(self):
        # Check for level ups
        while (self.upgrade_points > 0):
            eff_level = self.xp_level - self.upgrade_points
            stat_ind = self.upgrade_point_path[eff_level]
            self.upgradeStat(stat_ind)
            self.upgrade_points -= 1
        while self.evolve_upgrade_points > 0:
            self.changeTankType(self.evolve_path[self.evolve_path.index(self.tank_type)+1])
            self.evolve_upgrade_points -= 1
            self.intro_func(self, self.tank_type)
    def upgradeStat(self,stat_ind):
        if self.upgrade_points > 0:
            self.tank_stats[stat_ind] += 1
            self.upgrade_points -= 1
            self.assignStats()
            return True
        return False
    def faceTowards(self,r_co):

        t = twoCoAngle(self.pos, r_co)
        p = self.orientation
        right_rot = (t-p)%(2*pi)
        left_rot = (p-t)%(2*pi)

        if right_rot > left_rot: self.ori_vel -= min([BOT_ROT_ACC_MAG,BOT_ROT_ACC_LIMITER*right_rot,BOT_ROT_ACC_LIMITER*left_rot])
        else: self.ori_vel += min([BOT_ROT_ACC_MAG,BOT_ROT_ACC_LIMITER*right_rot,BOT_ROT_ACC_LIMITER*left_rot])






    

class Food(CollisionObject):
    DRAW_CODE = DRW_FOOD
    name = "Food"
    team = TEAM_NULL
    density = DNSTY_FOOD
    def __init__(self,game,food_code, start_pos):
        self.sides = SHP_SIDES[food_code]
        self.col = SHP_COLS[food_code]
        self.side_length = SHP_SIZES[food_code]
        self.max_health = self.health = SHP_HEALTH[food_code]
        self.food_code = food_code
        self.pos = start_pos
        self.vel = [0,0]
        self.rot_vel = 0
        self.col_dmg = 1
        self.dmg_ticks = 0
        self.rotation = 0

        super().__init__(game)
        self.o_poly, self.r, self.o_col_poly, self.col_r, self.o_col_rads = generatePolygon([0,0], self.side_length, self.sides, randrange(0,360))
        self.updatePolys()

        self.mass = self.density*polyArea(self.sides, self.side_length)
        self.mOI = self.mass * self.r #uses fake mOI 
        #Real mOI: self.mass * self.r**2 / 24 * (1 + 3*cot2(PI/self.sides))
    def update(self):
        self.game.chunkManager.update_obj(self)
        self.dmg_ticks = max(self.dmg_ticks-1,0)

        if vecMag(self.vel) >= FOOD_VEL_TOLERANCE or abs(self.rot_vel) >= FOOD_ROT_VEL_TOLERANCE:
            self.pos = dA(self.pos, self.vel)
            self.vel = dSM(FOOD_DRAG, self.vel)

            self.rotation += self.rot_vel
            self.rot_vel *= FOOD_ROT_DRAG
            self.rot_vel = min(self.rot_vel, MAX_FOOD_ROT_VEL)
            self.updatePolys()
        else:
            self.rot_vel = 0
            self.vel = [0,0]
    def updatePolys(self):
        shift = self.pos[:]
        self.col_rads = self.o_col_rads + self.rotation*2*PI  #FIXME check if the hitboxes still work
        self.poly = [dA(shift,vecRot(co,self.rotation)) for co in self.o_poly]
        self.col_poly = [dA(shift,vecRot(co,self.rotation)) for co in self.o_col_poly]
    def kill(self):
        self.game.killFood(self)
    def hitBy(self,col_obj):
        self.health = max(0, self.health - col_obj.col_dmg)
        self.dmg_ticks = DMG_ANIMATION_DURATION
        if self.health == 0:
            if col_obj.DRAW_CODE in [DRW_TANK_BOT, DRW_TANK_PLR]: col_obj.reportKilled(self)
            elif col_obj.DRAW_CODE in [DRW_PROJ_BLT, DRW_PROJ_FLW]: col_obj.owner.reportKilled(self)
            return True
        else: return False
    

### Game Object
class Game:
    def __init__(self,chunkManager,mode="Deathmatch",teams=0):
        self.foods = set()
        self.bots = set()
        
        self.chunkManager = chunkManager
        chunkManager.game = self
        self.mode = mode
        self.teams = teams

        self.leaderboard = [] # [ [tank name, tank points, leaderboard num] || None , ... ]

        self.food_amount = 0
        self.bots_amount = 0
        for _ in range(STATIC_FOOD_NUM): self.generate_food()
        if teams == 0:
            for _ in range(STATIC_BOTS_NUM): self.generate_bot(team=TEAM_NULL)
        else:
            for t in range(teams):
                for _ in range(STATIC_BOTS_NUM//teams): self.generate_bot(team=t)

        self.message_log = [["Welcome to the game!", black, 180]]#[ [msg_string, col, ticks], ...]
    def update(self,ticks):
        self.chunkManager.runCollisions() #update collisions

        #update user
        if self.user != None:
            mCo = pygame.mouse.get_pos()
            self.user.faceTowards(self.camera.dToR(mCo))
            self.user.update()

        #update bots and food
        for f in [f for f in self.foods if f.update()][::-1]: self.killFood(f)
        
        to_remove = []
        for b in self.bots:
            b.controlAI(ticks)
            if b.update(): to_remove.append(b)
        for b in to_remove[::-1]: self.killBot(b)
            

        # update message log
        to_remove = []
        for c,msg in enumerate(self.message_log):
            msg[2] -= 1
            if msg[2] <= 0: to_remove.append(c)
        for ind in to_remove[::-1]: del self.message_log[ind]

        #update leaderboard every 5 seconds
        if (ticks%300) == 0: self.genLeaderboard()
    def killFood(self,f):
        self.food_amount -= 1
        self.generate_food()
        f.colKill()
        self.foods.remove(f)
        del f
    def killBot(self,b):
        self.bots_amount -= 1
        self.generate_bot(b.team)

        for pr in list(b.projs)[:]: b.killProj(pr)
        b.colKill()
        self.bots.remove(b)
        del b
    def randomPos(self,border=10):
        return [randrange(-MAP_CONSTANT+border, MAP_CONSTANT-border), randrange(-MAP_CONSTANT+border, MAP_CONSTANT-border)]
    def generate_food(self):
        tries = 0
        while ((tries == 0) or (not inRect(new_food.pos, MAP_RECT)) or (new_food.checkCollisions())) and tries < 100:
            if tries != 0: new_food.colKill()
            if randrange(0,100) < FOOD_HUB_CHANCE:
                hub = food_hubs[choice(food_hubs_w_inds)]
                new_food = Food(self, choice(hub[1]), randomCircular(hub[0],hub[2]))
            else:
                new_food = Food(self,choice(WEIGHTED_FOOD_CODES), self.randomPos())
            tries += 1
        if tries < 100:
            self.foods.add(new_food)
            self.food_amount += 1
            return True
        else:
            return False
    def generate_bot(self,team=TEAM_NULL):
        new_bot = Bot(self, self.randomPos(), "Basic", team)
        self.bots.add(new_bot)
        self.bots_amount += 1
    def onClick(self,m_co):
        if self.user != None:
            button_clicked = False
            if self.user.upgrade_points > 0:
                for c,rect in enumerate(PLAYER_STATS_RECTS):
                    if inRect(m_co,rect):
                        button_clicked = True
                        if self.user.tank_stats[c] < MAX_TANK_UPGRADE:
                            self.user.tank_stats[c] += 1
                            self.user.upgrade_points -= 1
                            self.user.assignStats()
            if not button_clicked and self.user.evolve_upgrade_points > 0:
                tank_evolve_names = TANK_UPGRADE_TREE[self.user.tank_type] if self.user.tank_type in TANK_UPGRADE_TREE else []
                for c,name in enumerate(tank_evolve_names):
                    rect = PLAYER_EVOLVE_SQUARES[c]
                    if inRect(m_co,rect):
                        button_clicked = True
                        self.user.evolve_upgrade_points -= 1
                        self.user.changeTankType(name)

            if not button_clicked: self.user.onClick(m_co)
    def addMessage(self,txt,col,duration):
        self.message_log.append([txt,col,duration])
    def genLeaderboard(self):
        sorted_tanks = sorted(list(self.bots)+([self.user] if self.user != None else []), key=lambda t : -t.xp_points_total)
        sorted_len = len(sorted_tanks)
        if self.user != None: player_rank = sorted_tanks.index(self.user) + 1
        if self.user == None or player_rank <= LEADERBOARD_LEN: self.leaderboard = [[sorted_tanks[c].name, int(sorted_tanks[c].xp_points_total), c+1] for c in range(LEADERBOARD_LEN)]
        elif player_rank+2 >= sorted_len: self.leaderboard = [[sorted_tanks[c].name, int(sorted_tanks[c].xp_points_total), c+1] for c in range(LEADERBOARD_LEN - 4)] + [None] + [[sorted_tanks[c].name, int(sorted_tanks[c].xp_points_total), c+1] for c in range(sorted_len-4,sorted_len)]
        else: self.leaderboard = [[sorted_tanks[c].name, int(sorted_tanks[c].xp_points_total), c+1] for c in range(LEADERBOARD_LEN - 4)] + [None] + [[sorted_tanks[c].name, int(sorted_tanks[c].xp_points_total), c+1] for c in range(player_rank-2,player_rank+1)]
        self.leaderboard = self.leaderboard[::-1]
### Camera Object


class Camera:
    minimapTransform = lambda self,co : dInt(dA(dSM(104,[ (i+MAP_CONSTANT)/(MAP_CONSTANT*2) for i in co ]),[3+MINIMAP_POS[0],3+MINIMAP_POS[1]]))
    def __init__(self, game, player_mode):
        self.game = game
        self.game.camera = self
        self.player_mode = player_mode
        self.zoom = 5
        self.offset = [0,0]
        self.target = None#needs to be instanstiated by other objects
    def onScroll(self,button):
        r_co = self.dToR(S_CENT)
        self.zoom *= ZOOM_STRENGTH if button == 4 else (1/ZOOM_STRENGTH)
        self.zoom = limit(self.zoom, ZOOM_RANGE[1], ZOOM_RANGE[0])
        self.watchAt(r_co,S_CENT)
    def rToD(self, r_co,override_zoom=None):
        zoom = override_zoom if override_zoom != None else self.zoom
        return [zoom*i + self.offset[c] for c,i in enumerate(r_co)]
    def dToR(self, d_co,override_zoom=None):
        zoom = override_zoom if override_zoom != None else self.zoom
        return [(i-self.offset[c])/zoom for c,i in enumerate(d_co)]
    def watchAt(self, r_co, d_co):
        self.offset = [d_co[c] - self.zoom*r_co[c] for c in range(2)]
    def setTarget(self, t):
        self.target = t
    def renderObj(self,obj,override_zoom=None):
        zoom = override_zoom if override_zoom != None else self.zoom
        obj_type = obj.DRAW_CODE
        if obj_type == DRW_TANK_PLR:
            face_dir = ciS(1,obj.orientation)
            for t in obj.turrets:
                if t.proj_type == Follower:
                    t_dir           = vecRot(face_dir, t.orientation)
                    t_dir_left      = dM([(t.width/2)]*2, vecRotLeft(t_dir) )
                    t_dir_right     = dM([(t.width/2)]*2, vecRotRight(t_dir))
                    t_dir_forward   = dM([t.length]*2, t_dir)
                    poly = [dA(obj.pos,co) for co in [dSM(0.3,t_dir_left), dA(dSM(1.8,t_dir_left),t_dir_forward), dA(dSM(1.8,t_dir_right),t_dir_forward),dSM(0.3,t_dir_right)]]
                    self.showPolygon(poly,[80]*3,2,[120]*3, zoom)
                elif t.proj_type == Bullet:
                    t_dir           = vecRot(face_dir, t.orientation)
                    t_dir_left      = dM([(t.width/2)]*2, vecRotLeft(t_dir) )
                    t_dir_right     = dM([(t.width/2)]*2, vecRotRight(t_dir))
                    t_dir_forward   = dM([t.length]*2, t_dir)
                    tur_root = dA(obj.pos, dSM(t.perp_offset,vecRotLeft(t_dir)))
                    poly = [dA(tur_root,co) for co in [t_dir_left, dA(t_dir_left,t_dir_forward), dA(t_dir_right,t_dir_forward),t_dir_right]]
                    self.showPolygon(poly,[80]*3,2,[120]*3, zoom)
            self.showCircle(obj.pos, obj.col, obj.radius, 2, black, zoom)
            if obj.health < obj.max_health: healthBar(self.rToD(dA([-HB_WIDTH/2,obj.radius*1.2],obj.pos)),HB_WIDTH*zoom,HB_HEIGHT*zoom,2,green,[80]*3,red,obj.health/obj.max_health)
        elif obj_type == DRW_TANK_BOT:
            face_dir = ciS(1,obj.orientation)
            for t in obj.turrets:
                if t.proj_type == Follower:
                    t_dir           = vecRot(face_dir, t.orientation)
                    t_dir_left      = dM([(t.width/2)]*2, vecRotLeft(t_dir) )
                    t_dir_right     = dM([(t.width/2)]*2, vecRotRight(t_dir))
                    t_dir_forward   = dM([t.length]*2, t_dir)
                    poly = [dA(obj.pos,co) for co in [dSM(0.3,t_dir_left), dA(dSM(1.8,t_dir_left),t_dir_forward), dA(dSM(1.8,t_dir_right),t_dir_forward),dSM(0.3,t_dir_right)]]
                    self.showPolygon(poly,[80]*3,2,[120]*3,zoom)
                elif t.proj_type == Bullet:
                    t_dir           = vecRot(face_dir, t.orientation)
                    t_dir_left      = dM([(t.width/2)]*2, vecRotLeft(t_dir) )
                    t_dir_right     = dM([(t.width/2)]*2, vecRotRight(t_dir))
                    t_dir_forward   = dM([t.length]*2, t_dir)
                    tur_root = dA(obj.pos, dSM(t.perp_offset,vecRotLeft(t_dir)))
                    poly = [dA(tur_root,co) for co in [t_dir_left, dA(t_dir_left,t_dir_forward), dA(t_dir_right,t_dir_forward),t_dir_right]]
                    self.showPolygon(poly,[80]*3,2,[120]*3)
            self.showCircle(obj.pos, obj.col, obj.radius, 2, black,zoom)
            if obj.health < obj.max_health: healthBar(self.rToD(dA([-HB_WIDTH/2,obj.radius*1.2],obj.pos)),HB_WIDTH*zoom,HB_HEIGHT*zoom,2,green,[80]*3,red,obj.health/obj.max_health)
            dynamicMessageDisplay(obj.name,obj.col,int(round(obj.radius*NAME_TEXT_SIZE_MULT*zoom)),self.rToD(dA([0,-obj.radius*1.3],obj.pos)))
        elif obj_type == DRW_FOOD:
            if self.showPolygon(obj.poly, obj.col, 2, red if obj.dmg_ticks > 0 else black):
                if obj.health != obj.max_health:  healthBar(self.rToD(dA([-HB_WIDTH/2,obj.r*1.4],obj.pos)),HB_WIDTH*zoom,HB_HEIGHT*zoom,2,green,[80]*3,red,obj.health/obj.max_health)
        elif obj_type == DRW_PROJ_BLT:
            self.showCircle(obj.pos, obj.owner.col, obj.radius, 1, black)
        elif obj_type == DRW_PROJ_FLW:
            self.showPolygon(obj.poly, obj.col, 2, [210]*3 if obj.dmg_ticks > 0 else black)
    def showGrid(self):
        gridSize = int(200/1)
        tL = self.dToR((0,0))
        bR = self.dToR((dw,dh))

        for x in range(int(((tL[0])//200)*200),int(bR[0]),200):
            dX = x*self.zoom + self.offset[0]
            pygame.draw.line(screen,darkgreen,(dX,0),(dX,dh))

        for y in range(int(((tL[1])//200)*200),int(bR[1]),200):
            dY = y*self.zoom + self.offset[1]
            pygame.draw.line(screen,darkgreen,(0,dY),(dw,dY))
        yB = -MAP_CONSTANT*self.zoom + self.offset[1]
        if 0 <= yB <= dh: pygame.draw.rect(screen,BORDER_COLOUR,[0,0,dw,yB])
        xB = -MAP_CONSTANT*self.zoom + self.offset[0]
        if 0 <= xB <= dw: pygame.draw.rect(screen,BORDER_COLOUR,[0,0,xB,dh])
        yT = MAP_CONSTANT*self.zoom + self.offset[1]
        if 0 <= yT <= dh: pygame.draw.rect(screen,BORDER_COLOUR,[0,yT,dw,dh-yT])
        xT = MAP_CONSTANT*self.zoom + self.offset[0]
        if 0 <= xT <= dw: pygame.draw.rect(screen,BORDER_COLOUR,[xT,0,dw-xT,dh])
    def showCircle(self,pos,colour,radius,outline=0,outline_colour=None,override_zoom=None):
        zoom = override_zoom if override_zoom != None else self.zoom
        centre_d_pos = [int(round(i)) for i in self.rToD(pos,zoom)]
        if inRect(centre_d_pos, EX_S_RECT):
            size_d = zoom*radius
            pygame.draw.circle(screen,colour,centre_d_pos,size_d)
            if outline > 0:
                pygame.draw.circle(screen,outline_colour,centre_d_pos,size_d,outline)
            return True
        return False
    def showPolygon(self,poly,colour,outline=0,outline_colour=None,override_zoom=None):
        zoom = override_zoom if override_zoom != None else self.zoom
        poly_d_pos = [self.rToD(i,zoom) for i in poly]
        if any([inRect(i, EX_S_RECT) for i in poly_d_pos]): 

            pygame.draw.polygon(screen,colour,poly_d_pos)
            #pygame.draw.aalines(screen,colour, True, poly_d_pos)
            if outline > 0:
                pygame.draw.aalines(screen,outline_colour, True, poly_d_pos)
                #pygame.draw.polygon(screen,outline_colour,poly_d_pos,outline) #FUCKING BUG IM LEAVING THIS COMMENT IN THIS WAS SO FCKNG ANNOYING TO FIX FIXME
            return True
        return False   
    def showOverlay(self,fps=0):
        #minimap
        pygame.draw.rect(screen,white,MINIMAP_POS + [110,110])
        pygame.draw.rect(screen,black,MINIMAP_POS + [110,110],2)
        minimap_bR = dA(MINIMAP_POS,[108,108])
        for bots in self.game.bots: pygame.draw.circle(screen, bots.col, self.minimapTransform(bots.pos),3 )
        if self.game.user != None: pygame.draw.circle(screen,self.user.col,self.minimapTransform(self.user.pos),3)
        pygame.draw.polygon(screen, black, [dLimit(self.minimapTransform(self.dToR(co)),minimap_bR,MINIMAP_POS) for co in S_CORNER_POS], 1)

        if self.player_mode != "Spectator":
            #xp bar
            pygame.draw.rect(screen,black,[XPB_POS,dh-50,XPB_LENGTH,30])
            pygame.draw.rect(screen,yellow,[XPB_POS+2,dh-48,(XPB_LENGTH-4)*min(self.user.xp_points/self.user.xp_points_needed,1),26])
            messageDisplay("Lvl " + str(self.user.xp_level),[120,20,230],[dw//2,dh-35])

            #player stats
            if self.user.upgrade_points > 0 or pygame.key.get_pressed()[pygame.K_TAB]:
                if self.user.upgrade_points > 0: simpleText("Points: " + str(self.user.upgrade_points), PLAYER_STATS_POINTS_POS, colour=black)
                for c,rect in enumerate(PLAYER_STATS_RECTS):
                    pygame.draw.rect(screen,black,rect, border_radius=3)
                    pygame.draw.rect(screen,[180]*3,rect,2, border_radius=3)
                    for c_1 in range(self.user.tank_stats[c]): pygame.draw.rect(screen,[160,30,30],[rect[0]+5+25*c_1,rect[1]+5,20,20])
                    messageDisplay(str(TANK_STATS_NAMES[c]),white,rectCent(rect))

            #evolve previews
            if self.user.evolve_upgrade_points > 0:
                tank_evolve_names = TANK_UPGRADE_TREE[self.user.tank_type] if self.user.tank_type in TANK_UPGRADE_TREE else []
                for c,name in enumerate(tank_evolve_names):
                    rect = PLAYER_EVOLVE_SQUARES[c]
                    cent = rectCent(rect)
                    pygame.draw.rect(screen,black,rect, border_radius=5)
                    pygame.draw.rect(screen,[180]*3,rect,2, border_radius=5)
                    preview_tank = PLAYER_EVOLVE_PREVIEWS[name]
                    preview_tank.pos = self.dToR(cent,override_zoom=TANK_PREVIEW_ZOOM[name])
                    preview_tank.orientation += PREVIEW_ROT_SPEED

                    self.renderObj(preview_tank,override_zoom=TANK_PREVIEW_ZOOM[name])

                    messageDisplay(name,white,dA(rectCent(rect),[0,-rect[3]//3]))
        
        #show message log
        msgs = len(self.game.message_log)
        for c,msg in enumerate(self.game.message_log):
            simpleText(msg[0], dA(MESSAGE_LOG_POS,[0,(-msgs+c)*50]), msg[1], font=fancyFont)

        #show leaderboard
        #self.leaderboard = [] # [ [tank name, tank points, leaderboard num] || None , ... ]
        for c,entry in enumerate(self.game.leaderboard):
            if entry == None: simpleText("...", dA(LEADERBOARD_POS,[50,(-c)*40]), black, font=fancyFont)
            else:
                simpleText('#'+str(entry[2]), dA(LEADERBOARD_POS,[0,(-c)*40]), black, font=fancyFont)
                simpleText(entry[0], dA(LEADERBOARD_POS,[50,(-c)*40]), black, font=fancyFont)
                simpleText(str(entry[1]), dA(LEADERBOARD_POS,[250,(-c)*40]),  black, font=fancyFont)

        #fps
        simpleText("FPS: " + str(round(fps,2)),(dw-260,10),red)
    def show(self,fps=0):

        self.watchAt(self.target.pos, S_CENT)
        screen.fill(white)
        self.showGrid()

        nearby_objs = self.game.chunkManager.getInRect(self.dToR([0,0]), self.dToR([dw,dh]))
        for valid_draw_codes in DRW_ORDER:
            for obj in nearby_objs:
                if obj.DRAW_CODE in valid_draw_codes: self.renderObj(obj)

        self.showOverlay(fps)
        
        #2560 1440 DIMS

        # pygame.draw.polygon(screen, black,[[2584.969205043709, 636.3562709380935], [2613.894647479603, 601.8842709977398], [2590.048280589109, 563.7221066707007], [2546.3849729066887, 574.6085919726856], [2543.2459315882033, 619.4989742343778]],3) THIS IS AN EXAMPLE OF THE BUG!!!!!!
        # pygame.draw.aalines(screen, red, False, [[2584.969205043709, 636.3562709380935], [2613.894647479603, 601.8842709977398], [2590.048280589109, 563.7221066707007], [2546.3849729066887, 574.6085919726856], [2543.2459315882033, 619.4989742343778], [2584.969205043709, 636.3562709380935]],3)


##################################################################
###                        MENU SETUP                          ###
##################################################################


    
class MenuButton:
    def __init__(self,rect,text,func,font=fancyFont,rounding=-1):
        self.rect,self.text,self.func, self.font, self.rounding = rect,text,func,font, rounding
        self.cent = rectCent(rect)
    def inButton(self,m_co):
        return inRect(m_co, self.rect)
    def onPress(self):
        if self.func != None: self.func()
        return True
    def draw(self, m_co):
        selCol = [90]*3 if inRect(m_co,self.rect) else white
        pygame.draw.rect(screen,selCol,self.rect, border_radius = self.rounding)
        pygame.draw.rect(screen,black,self.rect,2, border_radius = self.rounding)
        centText(self.text,self.cent, black,font=self.font)


def pauseMenu():
    menu_exit = False
    screen.blit(pause_surface,[0,0])
    while not menu_exit:
        m_co = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); quit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if inRect(m_co,quit_button.rect):
                    return True
                if inRect(m_co,play_button.rect):
                    return False

        
        play_button.draw(m_co)
        quit_button.draw(m_co)
        PDU()
        
        clock.tick(30)

pause_surface = pygame.Surface([dw,dh],pygame.SRCALPHA,32)
pause_surface.fill([0,0,0,128])

def quit_func(): pygame.quit(); quit()
quit_button = MenuButton([dw-45,10,30,30],"X", lambda:True )
play_button = MenuButton([dw-45-40,10,30,30],"|>",lambda:True )
pause_button = MenuButton([dw-45-40,10,30,30],"||",pauseMenu )
start_button = MenuButton([dw//2-300,dh//2-60-250, 600, 120],"Start",lambda:True, big_font, 5)

option_rects = [[dw//2 - 100, dh//2-150+50*c, 200, 40] for c in range(3)]
option_cents = [rectCent(rect) for rect in option_rects]

left_option_rects = [dA(option_rects[c][:2],[-50,0]) + [40,40] for c in range(3)]
left_option_cents = [rectCent(rect) for rect in left_option_rects]

right_option_rects = [dA(option_rects[c][:2],[210,0]) + [40,40] for c in range(3)]
right_option_cents = [rectCent(rect) for rect in right_option_rects]

#VAPOUR SETUP

ver_surface = pygame.Surface([dw,dh])
ver_surface.fill(VER_LAND_COL)
step = dw//10
n = 0
for x in range(-dw*20,dw*21,step):
    if n%2 == 0:
        pygame.draw.line(ver_surface,VER_LINE_COL,(x,dh+1),(dw//2,HORIZON_LINE))
    n += 1
pygame.draw.rect(ver_surface,VER_SKY_COL,[0,0,dw,HORIZON_LINE+15])

class Menu:
    def __init__(self):
        self.phase = 1 #0 - intro menu phase | 1 - in game phase
        self.in_game_buttons = [quit_button, pause_button]
        self.menu_buttons = [quit_button, start_button]

        self.mode_options = ["Deathmatch", "Area Capture", "Rogue"]
        self.type_options = ["Player", "Spectator", "Pro", "God"]
        self.team_options = ["0","2","4"]

        self.option_inds = [0,0,0]
        self.option_strings = [self.mode_options, self.type_options, self.team_options]
    def getCurrentButtons(self):
        if self.phase == 0: return self.menu_buttons
        elif self.phase == 1: return self.in_game_buttons
    def show(self, m_co):
        for b in self.getCurrentButtons():
            b.draw(m_co)

    def setPhase(self,phase):
        self.phase = phase
    def mainMenu(self):
        menu_exit = False
        self.phase = 0
        ticks = 0
        while not menu_exit:
            keys_pressed = pygame.key.get_pressed()
            m_co = pygame.mouse.get_pos()
            options = [self.option_strings[c][self.option_inds[c]] for c in range(3)]
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); quit()

                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    if ev.button == 1:
                        if quit_button.inButton(m_co): pygame.quit(); quit()
                        elif start_button.inButton(m_co):
                            self.phase = 1
                            main_loop(*options)
                            self.phase = 0
                        else:
                            for c in range(3):
                                if inRect(m_co, left_option_rects[c]): 
                                    self.option_inds[c] = (self.option_inds[c]-1)%(len(self.option_strings[c]))
                                    if c == 0:
                                        if self.option_inds[0] == 2: self.team_options = ["0"]; self.option_inds[2] = 0 #Rogue
                                        elif self.option_inds[0] == 1:  self.team_options = ["2","4"]; self.option_inds[2] = (self.option_inds[2]+1)%2 #Area Capture
                                        else: self.team_options = ["0","2","4"] #TDM
                                        self.option_strings[2] = self.team_options
                                elif inRect(m_co, right_option_rects[c]): 
                                    self.option_inds[c] = (self.option_inds[c]+1)%(len(self.option_strings[c]))
                                    if c == 0:
                                        if self.option_inds[0] == 2: self.team_options = ["0"]; self.option_inds[2] = 0 #Rogue
                                        elif self.option_inds[0] == 1:  self.team_options = ["2","4"]; self.option_inds[2] = (self.option_inds[2]+1)%2 #Area Capture
                                        else: self.team_options = ["0","2","4"] #TDM
                                        self.option_strings[2] = self.team_options

                elif ev.type == pygame.KEYDOWN:
                    if ev.key in [pygame.K_LALT,pygame.K_RALT] and keys_pressed[pygame.K_F4]: pygame.quit(); quit()

            screen.fill(VER_LAND_COL)
            ### vapour wave render
            screen.blit(ver_surface,(0,0))
            z = 1-(ticks%30)/30
            while z < 1000:
                zP = 500/z+dh/2-15
                pygame.draw.line(screen,VER_LINE_COL,(0,zP),(dw,zP))
                z += 1
            # pygame.draw.line(screen, red, [0,HORIZON_LINE+15], [dw,HORIZON_LINE+15])
            pygame.draw.rect(screen,VER_SKY_COL,[0,0,dw,HORIZON_LINE+20])

            self.show(m_co)

            for c,option in enumerate(options):
                pygame.draw.rect(screen, [100,100,100], option_rects[c], border_radius=5)
                pygame.draw.rect(screen, [130,130,130], option_rects[c], 2, border_radius=5)
                centText(option, option_cents[c], colour=black)

                pygame.draw.rect(screen, [100,100,100], left_option_rects[c], border_radius=5)
                pygame.draw.rect(screen, [130,130,130] if inRect(m_co, left_option_rects[c]) else [70,70,70], left_option_rects[c], border_radius=5)
                centText('<', left_option_cents[c], colour=black)

                pygame.draw.rect(screen, [100,100,100], right_option_rects[c], border_radius=5)
                pygame.draw.rect(screen, [130,130,130] if inRect(m_co, right_option_rects[c]) else [70,70,70], right_option_rects[c], border_radius=5)
                centText('>', right_option_cents[c], colour=black)

            PDU()
            clock.tick(30); ticks += 1

##################################################################
###                       GAME SETUP                           ###
##################################################################

#setup food hubs
food_hubs = [ [(0,0), FOOD_HUB_CODES[-1], FOOD_HUB_RADII[-1]] ] #( [POS, CODES, RADIUS], ... )
food_hubs_w_inds = [0]
for n in range(1,FOOD_HUB_N+1):
    hub_type_ind = choice(FOOD_HUB_W_INDS)
    codes, radius, freq = FOOD_HUB_CODES[hub_type_ind], FOOD_HUB_RADII[hub_type_ind], FOOD_HUB_FREQ[hub_type_ind]

    try_pos = randomInRect(FOOD_HUB_RECT)
    while any([coDistance(try_pos,hub[0]) <= radius+hub[2]+FOOD_HUB_SEPERATION for hub in food_hubs]): try_pos = randomInRect(FOOD_HUB_RECT) #could get stuck on an infinite loop here, be careful!

    food_hubs.append([try_pos, codes, radius])
    food_hubs_w_inds += [n]*freq




##################################################################
###                       GAME LOOP                            ###
##################################################################

#main loop
""""
===game_type - reflects rules and goal of the game
    Values: Deathmatch, Area Capture, Rogue
===player_mode - reflects state of player
    Values: Player, Spectator, Pro, God
===game_teams - reflects amount of teams
    Values: 0 (FFA), 2, 4
    Must be 2,4 for game_type == Area Capture
    Must be 0 for game_type == Rogue
"""
def main_loop(game_type = "Deathmatch", player_mode = "Spectator", game_teams =  "0"):
    #instansiate classes and vars based on game type, player mode, and teams num
    game_teams = int(game_teams)
    chnkMngr = ChunkManager()

    #set up game based on game_type and game_teams
    if game_type == "Deathmatch":
        game = Game(chnkMngr, game_type, game_teams)
        for t in list(game.bots): t.addXP(randrange(0,5000))
    elif game_type == "Area Capture":
        pass#TODO
    elif game_type == "Rogue":
        pass#TODO

    #set up camera
    camera = Camera(game, player_mode)

    #set up player evolve previews
    global PLAYER_EVOLVE_PREVIEWS
    PLAYER_EVOLVE_PREVIEWS = dict()
    for tank_name in ALL_TANK_NAMES: PLAYER_EVOLVE_PREVIEWS[tank_name] = Player(game, camera, [0,0], tank_name,preview=True)

    #set up user based on player mode, and set camera target
    if player_mode in ["Player","Pro","God"]:
        user = Player(game, camera, [MAP_CONSTANT//2, MAP_CONSTANT//2], "Basic", TEAM_NULL if game_teams == 0 else randrange(0,game_teams), preview=False)
        if player_mode in ["Pro", "God"]: user.addXP(10000000)
        if player_mode == "God": user.upgrade_points += (MAX_TANK_UPGRADE*TANK_STATS_LEN - MAX_LEVEL)
        camera.setTarget(user)
    if player_mode == "Spectator":
        user = None
        game.user = None
        camera.user = None
        spec_ind = 0
        spec_pos = DummyPosition(list(game.bots)[spec_ind].pos)
        free_cam = False
        cam_speed = 1
        camera.setTarget(list(game.bots)[spec_ind])
        
        

    #set up final loop vars
    ticks = 0
    game_exit = False

    while not game_exit and (user == None or not user.isDead()):
        keys_pressed = pygame.key.get_pressed()
        m_co = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); quit()

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: 
                    if quit_button.inButton(m_co):
                        game_exit = True
                        continue
                    elif pause_button.inButton(m_co):
                        game_exit = pauseMenu()
                        if game_exit: continue
                    else:
                        game.onClick(ev.pos)
                elif ev.button in [4,5]: camera.onScroll(ev.button)

            elif ev.type == pygame.KEYDOWN:
                if player_mode == "Spectator":
                    if ev.key == pygame.K_LEFT: 
                        spec_ind = (spec_ind - 1) % len(game.bots)
                        camera.setTarget(list(game.bots)[spec_ind])
                    elif ev.key == pygame.K_RIGHT: 
                        spec_ind = (spec_ind + 1) % len(game.bots)
                        camera.setTarget(list(game.bots)[spec_ind])
                    elif ev.key == pygame.K_SPACE:
                        if free_cam == False:
                            free_cam = True
                            spec_pos.pos = list(game.bots)[spec_ind].pos
                            camera.setTarget(spec_pos)
                        else:
                            free_cam = False
                            camera.setTarget(list(game.bots)[spec_ind])
                else:
                    if ev.key in [pygame.K_LALT,pygame.K_RALT] and keys_pressed[pygame.K_F4]: pygame.quit(); quit()
                    else: user.onPress(ev.key)


        if user != None: user.onPressed(keys_pressed)
        game.update(ticks)

        if player_mode == "Spectator" and free_cam:
            
            for k in M_DI:
                if keys_pressed[k]: spec_pos.vel = dA(spec_pos.vel, dSM(cam_speed,M_DI[k]))
            spec_pos.pos = dA(spec_pos.pos, spec_pos.vel)
            spec_pos.vel = dSM(0.90,spec_pos.vel)

        fps = clock.get_fps()
        camera.show(fps)

        menu.show(m_co)

        PDU()

        clock.tick(60); ticks += 1


menu = Menu()
menu.mainMenu()


