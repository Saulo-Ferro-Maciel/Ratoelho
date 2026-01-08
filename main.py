import pgzrun
import math
import sys

WIDTH = 800
HEIGHT = 600
TITLE = "Ratoelho vs Pollos"

# =====================
# ÁUDIO 
# =====================
try:
    sounds.saulobeats.play(-1)
except Exception as e:
    print(f"Erro ao tocar áudio: {e}")

# Configurações de Chão
TILE_W = Actor('chao_principal').width
TILE_H = Actor('chao_principal').height
GROUND_Y = HEIGHT - TILE_H + 20 
WORLD_WIDTH = 2400 
GRAVITY = 0.5

# =====================
# ASSETS
# =====================
RATOELHO_IDLE_RIGHT = ['ratoelho/indle_0']
RATOELHO_WALK_RIGHT = ['ratoelho/walk_1','ratoelho/walk_2','ratoelho/walk_3','ratoelho/walk_4','ratoelho/walk_5']
RATOELHO_IDLE_LEFT  = ['ratoelho/indle_0_left']
RATOELHO_WALK_LEFT  = ['ratoelho/walk_1_left','ratoelho/walk_2_left','ratoelho/walk_3_left','ratoelho/walk_4_left','ratoelho/walk_5_left']

POLLO_WALK_RIGHT   = ['pollo/pollo_walk_1.png','pollo/pollo_walk_2.png','pollo/pollo_walk_3.png']
POLLO_WALK_LEFT    = ['pollo/pollo_walk_1_r.png','pollo/pollo_walk_2_r.png','pollo/pollo_walk_3_r.png']
POLLO_ATTACK_RIGHT = ['pollo/pollo_atackk.png']
POLLO_ATTACK_LEFT  = ['pollo/pollo_atackk_r.png']

# =====================
# ESTADOS GLOBAIS
# =====================
player = Actor(RATOELHO_IDLE_RIGHT[0], (100, GROUND_Y - 45))
player.speed = 5
player.vy = 0
player.on_ground = True
player.dir = 'right'

JUMP_SPEED = -11
pollos, eggs, platforms, pedestals, carrots = [], [], [], [], []
score, hp, current_level, t, camera_x = 0, 100, 1, 0, 0
game_state = 'menu'
intro_timer = 0 

jogar_btn  = Rect((WIDTH//2 - 100, 220), (200, 60))
sobre_btn  = Rect((WIDTH//2 - 100, 300), (200, 60))
sair_btn   = Rect((WIDTH//2 - 100, 380), (200, 60))
voltar_btn = Rect((WIDTH//2 - 100, 500), (200, 50))

# =====================
# MECÂNICAS
# =====================
def spawn_pollo(x, y=None):
    if y is None: y = GROUND_Y - 100
    p = Actor('pollo/pollo_indle', (x, y))
    p.dir, p.speed, p.state, p.attack_timer = 1, 1.2, 'walk', 0
    p.vy = 0
    pollos.append(p)

def start_level(lvl):
    global current_level, WORLD_WIDTH, pollos, carrots, pedestals, platforms, eggs, camera_x, intro_timer
    current_level = lvl
    pollos.clear(); carrots.clear(); pedestals.clear(); platforms.clear(); eggs.clear()
    camera_x = 0
    player.pos = (100, GROUND_Y - 45)
    if lvl == 1: intro_timer = 600 

    if lvl == 1:
        WORLD_WIDTH = 1600
        p1 = Actor('pedestal', (400, GROUND_Y - 15)); pedestals.append(p1); add_carrot_on(p1)
        add_platform(650, 420); add_platform(950, 320)
        spawn_pollo(700); spawn_pollo(1000)
    elif lvl == 2:
        WORLD_WIDTH = 2400
        for x in range(400, 2200, 450): spawn_pollo(x)
        for x in range(500, 2000, 600):
            p = Actor('pedestal', (x, GROUND_Y - 15)); pedestals.append(p); add_carrot_on(p)
            add_platform(x + 250, 380)
    elif lvl == 3:
        WORLD_WIDTH = 3200
        for x in range(300, 3000, 350): spawn_pollo(x)
        for x in range(400, 3000, 500):
            plat_y = 450 if x % 1000 == 0 else 350
            add_platform(x, plat_y)
            spawn_pollo(x, plat_y - 80)

def add_platform(x, y):
    plat = Actor('plataforma', (x, y))
    platforms.append(plat)
    return plat

def add_carrot_on(actor, offset=55):
    c = Actor('cenoura', (actor.x, actor.y - offset))
    c.base_y = c.y
    carrots.append(c)

# =====================
# LÓGICA PRINCIPAL
# =====================
def update():
    global t, score, hp, game_state, camera_x, intro_timer
    if game_state != 'game': return
    if intro_timer > 0:
        intro_timer -= 1
        return 

    t += 1
    moving = False
    
    # Movimento Player
    if keyboard.left or keyboard.a: 
        player.x -= player.speed
        player.dir, moving = 'left', True
    if keyboard.right or keyboard.d: 
        player.x += player.speed
        player.dir, moving = 'right', True
    if (keyboard.up or keyboard.w) and player.on_ground: 
        player.vy = JUMP_SPEED
        player.on_ground = False

    player.vy += GRAVITY
    player.y += player.vy

    # Animação do Ratoelho
    if moving:
        player.image = RATOELHO_WALK_RIGHT[(t//6)%5] if player.dir == 'right' else RATOELHO_WALK_LEFT[(t//6)%5]
    else:
        player.image = RATOELHO_IDLE_RIGHT[0] if player.dir == 'right' else RATOELHO_IDLE_LEFT[0]

    # Colisões Player
    if player.y >= GROUND_Y - 45: player.y, player.vy, player.on_ground = GROUND_Y - 45, 0, True
    for p in platforms:
        if player.colliderect(p) and player.vy > 0 and player.y < p.y:
            player.y, player.vy, player.on_ground = p.top - 40, 0, True

    # Lógica dos Pollos
    for p in pollos:
        p.vy += GRAVITY
        p.y += p.vy
        if p.y >= GROUND_Y - 35: p.y, p.vy = GROUND_Y - 35, 0
        for plat in platforms:
            if p.colliderect(plat) and p.vy > 0 and p.y < plat.y:
                p.y, p.vy = plat.top - 35, 0

        dx = player.x - p.x
        if p.state == 'walk':
            p.x += p.speed * p.dir
            if p.x < 100 or p.x > WORLD_WIDTH - 100: p.dir *= -1
            p.image = POLLO_WALK_LEFT[(t//12)%3] if p.dir > 0 else POLLO_WALK_RIGHT[(t//12)%3]
            if abs(dx) < 220: p.state = 'aim'
        elif p.state == 'aim':
            p.image = POLLO_ATTACK_RIGHT[0] if dx > 0 else POLLO_ATTACK_LEFT[0]
            p.attack_timer, p.state = 0, 'attack'
        elif p.state == 'attack':
            p.attack_timer += 1
            if p.attack_timer == 30:
                egg = Actor('egg', (p.x, p.y + 10))
                egg.vx, egg.vy = (6 if dx > 0 else -6), -4; eggs.append(egg)
            if p.attack_timer > 60: p.state = 'wait'
        elif p.state == 'wait' and abs(dx) > 300: p.state = 'walk'

    # Outros elementos
    for e in eggs[:]:
        e.x += e.vx; e.y += e.vy; e.vy += 0.2
        if player.colliderect(e): eggs.remove(e); hp -= 10
        elif e.y > HEIGHT: eggs.remove(e)

    for c in carrots[:]:
        c.y = c.base_y + math.sin(t * 0.1) * 8
        if player.colliderect(c): carrots.remove(c); score += 1

    player.x = max(20, min(WORLD_WIDTH - 20, player.x))
    camera_x = max(0, min(WORLD_WIDTH - WIDTH, player.x - WIDTH // 2))

    if player.x > WORLD_WIDTH - 60:
        if current_level < 3: start_level(current_level + 1)
        else: game_state = 'win'
    if hp <= 0: game_state = 'game_over'

def draw():
    screen.clear()
    if game_state == 'game':
        screen.fill((135, 206, 250))
        for x in range(-int(camera_x) % TILE_W - TILE_W, WIDTH + TILE_W, TILE_W):
            screen.blit('chao_principal', (x, HEIGHT - TILE_H))
        for ped in pedestals: screen.blit(ped.image, (ped.x - camera_x, ped.y))
        for obj in platforms + carrots + pollos + eggs:
            screen.blit(obj.image, (obj.x - camera_x, obj.y))
        screen.blit(player.image, (player.x - camera_x, player.y))
        
        # PLACAR RECUPERADO
        screen.draw.text(f"Fase: {current_level} | HP: {hp} | Score: {score}", (20,20), fontsize=32, color="black")
        
        if intro_timer > 0:
            box = Rect((WIDTH//2 - 250, HEIGHT//2 - 150), (500, 300))
            screen.draw.filled_rect(box, "white"); screen.draw.rect(box, "black")
            msg = f"FASE {current_level}\n\n3 Fases no total.\nChegue ao final da borda da tela direita!\n\nLiberando em: {math.ceil(intro_timer/60)}"
            screen.draw.text(msg, center=box.center, fontsize=30, color="black", align="center")

    elif game_state == 'menu':
        screen.draw.text("RATOELHO vs POLLOS", center=(WIDTH//2,120), fontsize=55, color="orange")
        for btn, txt, col in [(jogar_btn, "JOGAR", "green"), (sobre_btn, "SOBRE", "purple"), (sair_btn, "SAIR", "red")]:
            screen.draw.filled_rect(btn, col); screen.draw.text(txt, center=btn.center, fontsize=40, color="white")
    elif game_state == 'sobre':
        screen.fill((50, 50, 70))
        screen.draw.filled_rect(voltar_btn, "blue"); screen.draw.text("VOLTAR", center=voltar_btn.center, fontsize=30, color="white")
    elif game_state == 'game_over': screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="red")
    elif game_state == 'win': screen.draw.text("VITÓRIA!", center=(WIDTH//2, HEIGHT//2), fontsize=80, color="green")

def on_mouse_down(pos):
    global game_state, score, hp
    if game_state == 'menu':
        if jogar_btn.collidepoint(pos): game_state, score, hp = 'game', 0, 100; start_level(1)
        elif sobre_btn.collidepoint(pos): game_state = 'sobre'
        elif sair_btn.collidepoint(pos): sys.exit()
    elif game_state == 'sobre' and voltar_btn.collidepoint(pos): game_state = 'menu'
    elif game_state in ('game_over', 'win'): game_state = 'menu'

pgzrun.go()