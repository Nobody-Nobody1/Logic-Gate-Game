import pygame, sys, json, itertools

pygame.init()

WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Logic Simulator PRO")

font = pygame.font.SysFont(None, 20)

# ---------- Camera ----------
class Camera:
    def __init__(self):
        self.x=0; self.y=0
        self.zoom=1

    def apply(self,pos):
        return ((pos[0]+self.x)*self.zoom,
                (pos[1]+self.y)*self.zoom)

    def inv(self,pos):
        return (pos[0]/self.zoom - self.x,
                pos[1]/self.zoom - self.y)

cam=Camera()

# ---------- Colors ----------
WHITE=(255,255,255)
BLACK=(30,30,30)
GRAY=(210,210,210)
BLUE=(80,120,255)
GREEN=(0,200,0)
RED=(200,0,0)
YELLOW=(255,200,0)

# ---------- Port ----------
class Port:
    def __init__(self,parent,x,y,is_output=False):
        self.parent=parent
        self.x=x; self.y=y
        self.is_output=is_output
        self.value=0

    def pos(self):
        return (self.parent.x+self.x,
                self.parent.y+self.y)

# ---------- Components ----------
class Component:
    def __init__(self,x,y):
        self.x=x; self.y=y
        self.w=90; self.h=60
        self.selected=False

    def rect(self):
        return pygame.Rect(self.x,self.y,self.w,self.h)

class Input(Component):
    def __init__(self,x,y,name="A"):
        super().__init__(x,y)
        self.name=name
        self.value=0
        self.out=Port(self,90,30,True)

    def update(self):
        self.out.value=self.value

    def draw(self):
        r=self.rect()
        pygame.draw.rect(screen,BLUE if not self.selected else YELLOW,
                         (*cam.apply((r.x,r.y)),
                          r.w*cam.zoom,r.h*cam.zoom))

        txt=font.render(f"{self.name}:{self.value}",1,WHITE)
        screen.blit(txt,cam.apply((r.x+5,r.y+10)))

        pygame.draw.circle(screen,
            GREEN if self.value else RED,
            cam.apply(self.out.pos()),6)

class Gate(Component):
    def __init__(self,x,y,t):
        super().__init__(x,y)
        self.type=t
        self.out=Port(self,90,30,True)
        self.inputs=[Port(self,0,15),Port(self,0,45)]
        if t=="NOT":
            self.inputs=[Port(self,0,30)]

    def compute(self):
        vals=[p.value for p in self.inputs]
        if self.type=="AND": self.out.value=int(all(vals))
        elif self.type=="OR": self.out.value=int(any(vals))
        elif self.type=="XOR": self.out.value=int(sum(vals)%2)
        elif self.type=="NOT": self.out.value=int(not vals[0])

    def draw(self):
        r=self.rect()
        pygame.draw.rect(screen,BLACK if not self.selected else YELLOW,
                         (*cam.apply((r.x,r.y)),
                          r.w*cam.zoom,r.h*cam.zoom))

        txt=font.render(self.type,1,WHITE)
        screen.blit(txt,cam.apply((r.x+10,r.y+5)))

        for p in self.inputs:
            pygame.draw.circle(screen,
                GREEN if p.value else RED,
                cam.apply(p.pos()),5)

        pygame.draw.circle(screen,
            GREEN if self.out.value else RED,
            cam.apply(self.out.pos()),6)

# ---------- Wire ----------
class Wire:
    def __init__(self,a,b):
        self.a=a; self.b=b

    def update(self):
        self.b.value=self.a.value

    def draw(self):
        pygame.draw.line(screen,YELLOW,
            cam.apply(self.a.pos()),
            cam.apply(self.b.pos()),3)

# ---------- Globals ----------
components=[]
wires=[]
selected_port=None
drag=None
panning=False
last_mouse=(0,0)

show_truth=False

# ---------- Truth Table ----------
def compute_truth():
    ins=[c for c in components if isinstance(c,Input)]
    rows=[]
    for combo in itertools.product([0,1], repeat=len(ins)):
        for i,v in zip(ins,combo):
            i.value=v
        for c in components:
            if isinstance(c,Gate): c.compute()
        outputs=[c.out.value for c in components if isinstance(c,Gate)]
        rows.append((combo,outputs))
    return rows

# ---------- Main Loop ----------
while True:
    screen.fill(GRAY)

    # draw grid
    for x in range(0,WIDTH,40):
        pygame.draw.line(screen,(230,230,230),(x,0),(x,HEIGHT))
    for y in range(0,HEIGHT,40):
        pygame.draw.line(screen,(230,230,230),(0,y),(WIDTH,y))

    # update
    for c in components:
        if isinstance(c,Input): c.update()
        if isinstance(c,Gate): c.compute()

    for w in wires: w.update()

    # draw wires
    for w in wires: w.draw()

    # draw components
    for c in components:
        c.draw()

    # truth table UI
    if show_truth:
        rows=compute_truth()
        y=20
        for r in rows[:10]:
            txt=font.render(f"{r[0]} -> {r[1]}",1,BLACK)
            screen.blit(txt,(1000,y))
            y+=20

    # events
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            pygame.quit(); sys.exit()

        elif e.type==pygame.MOUSEBUTTONDOWN:
            mx,my=e.pos

            if e.button==2:
                panning=True
                last_mouse=(mx,my)

            if e.button==1:
                wx,wy=cam.inv((mx,my))

                # select
                for c in components:
                    if c.rect().collidepoint(wx,wy):
                        c.selected=True
                        drag=c
                    else:
                        c.selected=False

        elif e.type==pygame.MOUSEBUTTONUP:
            drag=None
            panning=False

        elif e.type==pygame.MOUSEMOTION:
            mx,my=e.pos

            if drag:
                wx,wy=cam.inv((mx,my))
                drag.x,drag.y=wx,wy

            if panning:
                dx=mx-last_mouse[0]
                dy=my-last_mouse[1]
                cam.x+=dx/50
                cam.y+=dy/50
                last_mouse=(mx,my)

        elif e.type==pygame.MOUSEWHEEL:
            cam.zoom*=1.1 if e.y>0 else 0.9

        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_a:
                components.append(Input(100,100,"A"))
            if e.key==pygame.K_g:
                components.append(Gate(200,200,"AND"))
            if e.key==pygame.K_t:
                show_truth=not show_truth

    pygame.display.flip()