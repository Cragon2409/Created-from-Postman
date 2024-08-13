import math
from random import randrange, seed, random, choice

### CONSTANTS
black = (0,0,0); lightgray = (150,150,150); darklightgray = (100,100,100); white = (255,255,255); red = (255,0,0); green = (0,255,0); blue = (0,0,255); darkgray = (50,50,50); brown = (101,67,33); darkorange = (255,100,0); darkgreen = (0,100,0); darkred = (139,0,0); yellow = (255,255,0); whiteskin = (255,195, 170); yellow = (255,255,0); darkyellow = (204,204,0); purple = (128,0,128); lightblue = (50,50,255); yellow = (230,240,20)
POLY_ADJUSTMENTS = [0,0,0,0,1/math.sqrt(2),0,1/(1.1547),0,1/1.08239,0,1/1.05146,0,1/1.03527,0,1/1.0257,0,1/1.01959,0,1/1.01542661189,0,1/1.012465]

PI = math.pi


### Text Rendering
def textObjects(text,font,colour=white):
    textSurface = font.render(text,True,colour)
    return(textSurface, textSurface.get_rect())


### Vector Handling

def limit(n,t,b): return min(t,max(n,b))
sign = lambda x : 1 if x >= 0 else -1
def reduce(x,r=0.97): return x*r

cot2 = lambda x : 1/(math.tan(x)**2)
def specReduce(x,r=0.97,s=0.1):
    o = x*r
    if -s <= o <= s: return 0
    return o

def dS(d1,d2): return [d1[0]-d2[0],d1[1]-d2[1]]
def dA(d1,d2): return [d1[0]+d2[0],d1[1]+d2[1]]
def dSM(s,d1): return [s*d1[0],s*d1[1]]
def dM(d1,d2): return [d1[0]*d2[0],d1[1]*d2[1]]
def dD(d1,d2): return [d1[0]/d2[0],d1[1]/d2[1]]
def dInt(d): return [int(d[0]), int(d[1])]
def dLimit(d,d_max,d_min): return [limit(d[n],d_max[n],d_min[n]) for n in range(2)]
def dMin(d_list): return [min([d[c] for d in d_list]) for c in range(2)]
def dMax(d_list): return [max([d[c] for d in d_list]) for c in range(2)]

def nupleAdd(d1,d2,le=5): return [d1[n]+d2[n] for n in range(le)]

def vecSub(co,d=1):
    co = list(co)
    if co == [0,0]: return [0,0]
    mag = d/math.sqrt(co[0]**2+co[1]**2)
    return [co[0]*mag,co[1]*mag]

def pos(x): return int(abs(x)/x)

def ciS(m,arg): return [m*math.cos(arg) , m*math.sin(arg)]

def cMult(a,b,c,d): return a*c - b*d, a*d + b*c

def vecRot(co,d=1): return cMult(*ciS(1,d*2*math.pi)+co)#1 is a full rotation

def vecRotLeft(co): return [-co[1], co[0]]

def vecRotRight(co): return [co[1], -co[0]]

def vecChange(co,mD,rD): return vecRot(vecSub(co,mD),rD)

def vecDot(v1,v2): return sum([v1[n]*v2[n] for n in range(2)])

def circleCo(x,r=90,n=360): return math.cos(2*math.pi/n*x)*r,math.sin(2*math.pi/n*x)*r

def inRect(co,rect): return co[0] >= rect[0] and co[1] >= rect[1] and co[0] < rect[0]+rect[2] and co[1] < rect[1]+rect[3]

def circleInRect(co,rect,radius): return co[0] >= rect[0]+radius and co[1] >= rect[1]+radius and co[0] < rect[0]+rect[2]-radius and co[1] < rect[1]+rect[3]-radius

def decRange(t,b):
    seed()
    return random()*(t-b)+b

def coDistance(co1,co2): return math.sqrt(sum([(co1[n]-co2[n])**2 for n in range(len(co1))]))

def midPoint(co1,co2): return [ (co1[n]+co2[n])/2 for n in range(2) ]

def tLBR(cos): return ( (min([i[0] for i in cos]) , min([i[1] for i in cos]))  ,  (max([i[0] for i in cos]) , max([i[1] for i in cos]))  )

def tL(cos): return [min([i[0] for i in cos]) , min([i[1] for i in cos])]

def listPhrase(li,i,pl):
    li = li[:]
    le = len(li)
    c = i
    c1 = pl
    nLi = [None for i in li]
    for x in li:
        nLi[c1] = li[c]
        c1 = (c1 + 1) % le
        c = (c + 1) % le
    return nLi

def decFloor(x,pl):return ((x*10**pl)//1)/(10**pl)

def closestRads(r,r0,r1): #return the number out of r0,r1 closest to r
    r0_dist = min((r-r0)%(2*PI), (r0-r)%(2*PI))
    r1_dist = min((r-r1)%(2*PI), (r1-r)%(2*PI))
    if r0_dist < r1_dist: return 0#r0
    else: return 1 #r1

def randomCircular(pos,max_dist): #uses integers
    dist = randrange(0,max_dist+1)
    angle = randrange(0,360)/(2*PI)
    return dA(pos,ciS(dist,angle))


def randomInRect(rect): #uses integers
    return [rect[0] + randrange(0,rect[2]+1), rect[1]+randrange(0,rect[3]+1)]

def decRandom():#-1 to 1
    return randrange(-1000,1001)/1000

def polyTranslate(co,si,pl,shapeSides,offRot=0):#generates a polygon
    internalAngle = 360/shapeSides
    #offRot = randrange(0,int(internalAngle))
    angles = [(-n*internalAngle+offRot)%360 for n in range(shapeSides)]
    out = [None for i in range(shapeSides)]
    pl = (pl - 1)%shapeSides
    for n in range(shapeSides):
        out[pl] = co
        co = dA(co,circleCo(angles[pl],si))
        pl = (pl + 1)%shapeSides
    return out

def perpGrad(co1,co2):
    if co1[1] == co2[1]: return None
    else: return -(co1[0]-co2[0])/(co1[1]-co2[1])

def normGrad(co1,co2):
    if co1[0] == co2[0]: return None
    else: return (co1[1]-co2[1])/(co1[0]-co2[0])

# def polyCentre(poly):
#     return circleGen(*poly[:3])
def polyCentre(poly,si):
    le = len(poly)
    return [sum([i[n] for i in poly])/le for n in range(2)]

def circleGen(p1,p2,p3):
    a,b,c,d,e,f = tuple(list(p1)+list(p2)+list(p3))
    if a == c: c,d,e,f = e,f,c,d
    if c == e: a,b,c,d = c,d,a,b
    Y = ( (b**2-d**2)/(2*(a-c)) + (a+c)/2 - (d**2-f**2)/(2*(c-e)) - (c+e)/2 ) / ( (f-d)/(c-e) - (d-b)/(a-c) )
    X = ( a**2-c**2 + (b-d)*(d+b-2*Y) ) / (2*(a-c))
    return (X,Y)#,r

def inLine(x,sCo,eCo):#assuming on gradient, checking range
    if sCo[0] != eCo[0]: return min(sCo[0],eCo[0]) < x < max(sCo[0],eCo[0])
    else: return
    
def circleLine(co1,co2,center,radius):
    out = False
    if co1[0] != co2[0]:
        m = (co1[1]-co2[1])/(co1[0]-co2[0]) 
        b = co1[1] - m*co1[0]
        denom = m**2 + 1
        disc = (b*m - m*center[1] - center[0])**2 - denom*(center[0]**2 + center[1]**2 + b**2 - 2*b*center[1] - radius**2)
        if disc >= 0:
            fNum = center[0] + m*center[1] - b*m
            disc = math.sqrt(disc)
            if inLine((fNum + disc)/denom,co1,co2) or inLine((fNum - disc)/denom,co1,co2): out = True
    else:
        n = co1[0]
        disc = radius**2 - (n-center[0])**2
        if disc >= 0:
            disc = math.sqrt(disc)
            miP = min(co1[1],co2[1]);  maP = max(co1[1],co2[1])
            if miP < center[1] + disc < maP or miP < center[1] -  disc < maP:
                out = True
    return out

def polyArea(n,s):#returns area 
    return (n*s**2) / (4 * math.tan(PI/n))

def rectCent(rect): return dA(rect[:2],dSM(0.5,rect[2:]))
def rectPoints(rect): return [rect[:2], dA(rect[:2], [rect[2],0]), dA(rect[:2], rect[2:]), dA(rect[:2], [0,rect[3]])]

def genRect(cent, dim): return dInt(dS(cent,dSM(0.5,dim))) + dim


def dRConv(r): return r* (PI/180)
def rDConv(d): return d* (180/PI)

def rTD(co,add,zoom): return [zoom*i + add[c] for c,i in enumerate(co)]
def dTR(co,add,zoom): return [(i-add[c])/zoom for c,i in enumerate(co)]

def twoCoAngle(co_1,co_2):
    vec = dS(co_2,co_1)
    if vec[0] == 0: return PI/2 if vec[1] >= 0 else 3*PI/2
    else:
        pre_rads = math.atan(vec[1]/vec[0])
        if vec[0] < 0: pre_rads += PI
        return (pre_rads) % (2*PI)


def vecAngle(vec):
    if vec[0] == 0: return PI if vec[1] >= 0 else 0
    else:
        pre_rads = math.atan(vec[1]/vec[0])
        if vec[0] < 0: pre_rads += PI
        return (pre_rads) % (2*PI)
    
def vecMag(vec):
    return math.sqrt(vec[0]**2 + vec[1]**2)

def generatePolygon(cent,side_length,side_n,rot_shift=0):
    poly =  polyTranslate([0,0],side_length,0,side_n,rot_shift)
    found_cent = polyCentre(poly,side_length)
    shift = dS(cent,found_cent)
    poly = [dA(shift,i) for i in poly]
    real_r = coDistance(cent,poly[0])

    if side_n%2 == 1:
        aPoly = [ midPoint(poly[n],poly[(n+1)%side_n]) for n in range(side_n)]
        r_a = coDistance(cent,aPoly[0])
        rads_a = twoCoAngle(cent,aPoly[0])
        return poly, real_r, aPoly, r_a, rads_a
    elif side_n < len(POLY_ADJUSTMENTS):
        rads = twoCoAngle(cent,poly[0])
        return poly, real_r, poly, real_r*POLY_ADJUSTMENTS[side_n], rads
    
sec2 = lambda x : 1 / math.cos(x)**2
def pointInPoly(co,polygon,centre,radius,rad_offset):
    vec = dS(centre,co)
    theta = vecAngle(vec)
    n = len(polygon)
    poly_radius = radius * math.sqrt(sec2(abs(((theta - rad_offset) % (2*PI/n)) - PI/n))) 
    return vecMag(vec) <= poly_radius

def circleInPoly(c_co,c_radius,true_polygon, col_polygon, centre, radius, rad_offset):
    if any([coDistance(c_co,co) <= c_radius for co in true_polygon]): return True
    else:
        use_dist = min(c_radius, coDistance(centre,c_co))
        towards_co = dA(c_co, vecSub(dS(centre,c_co),use_dist))
        return pointInPoly(towards_co, col_polygon, centre, radius, rad_offset) or pointInPoly(c_co, col_polygon, centre, radius, rad_offset)
    
def rectOverlapRect(rect_1, rect_2): return any([inRect(co,rect_1) for co in rectPoints(rect_2)]) or any([inRect(co,rect_2) for co in rectPoints(rect_1)]) or any([rect_1[c+0] < rect_2[c+0] and rect_1[c+0]+rect_1[c+2] > rect_2[c+0]+rect_2[c+2] for c in range(2)])

def roundNum(i_1, i_2):
    return (i_1//i_2)*i_2

WORD_LIST_1 = ["Cheese","Diamond","Fortnite","Roblox","Women","Men","Bannana","Pizza","Water",""]
CONNECTIVE_LIST = ['','','-','_']
WORD_LIST_2 = ["Lover","Hater","Haver","Player","Wanter","Pro","Expert","User","Consumer","Enjoyer", "God"]
def genUsername(): return choice(WORD_LIST_1) + choice(CONNECTIVE_LIST) + choice(WORD_LIST_2) + (str(randrange(1000,10000)) if randrange(0,2) == 0 else "")

def furtherPairDist(li): #list of cos
    all_dists = []
    le = len(li)
    for n in range(0,le-1):
        for n_1 in range(n+1,le):
            all_dists.append(coDistance(li[n], li[n_1]))
    return max(all_dists)
