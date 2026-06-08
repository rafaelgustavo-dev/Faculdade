# Sem instalação necessária — tkinter já vem com o Python

import tkinter as tk
import random
import math
import time

SCREEN_W, SCREEN_H = 1152, 720

BG        = '#1e1e1e'
DARK_GRID = '#373737'
ORANGE    = '#ff8c00'
AZURE     = '#50b4ff'
WHITE     = '#ffffff'
GRAY      = '#969696'
GREEN_HB  = '#00dc00'
RED_HB    = '#dc0000'

ESCALA  = 40
COS_ISO = math.cos(math.radians(30))
SIN_ISO = math.sin(math.radians(30))
CX = SCREEN_W // 2
CY = SCREEN_H // 2

ARESTAS = [
    (0,1),(1,2),(2,3),(3,0),
    (4,5),(5,6),(6,7),(7,4),
    (0,4),(1,5),(2,6),(3,7),
]

def para_tela(x, y, z):
    sx = CX + (x - z) * COS_ISO * ESCALA
    sy = CY - (x + z) * SIN_ISO * ESCALA + y * ESCALA * 0.85
    return sx, sy

def vertices_caixa(x, y, z, w, h, d):
    hw, hh, hd = w/2, h/2, d/2
    return [
        para_tela(x-hw, y-hh, z-hd),
        para_tela(x+hw, y-hh, z-hd),
        para_tela(x+hw, y-hh, z+hd),
        para_tela(x-hw, y-hh, z+hd),
        para_tela(x-hw, y+hh, z-hd),
        para_tela(x+hw, y+hh, z-hd),
        para_tela(x+hw, y+hh, z+hd),
        para_tela(x-hw, y+hh, z+hd),
    ]

def desenhar_caixa(canvas, verts, cor, espessura=2):
    for a, b in ARESTAS:
        canvas.create_line(
            verts[a][0], verts[a][1],
            verts[b][0], verts[b][1],
            fill=cor, width=espessura
        )

def aabb_colide(a, b):
    return (
        abs(a['x'] - b['x']) < (a['w'] + b['w']) / 2 and
        abs(a['y'] - b['y']) < (a['h'] + b['h']) / 2 and
        abs(a['z'] - b['z']) < (a['d'] + b['d']) / 2
    )

def criar_objeto(pos, tam, cor):
    return {
        'x': pos[0], 'y': pos[1], 'z': pos[2],
        'w': tam[0],  'h': tam[1],  'd': tam[2],
        'cor': cor, 'colidindo': False
    }

# --- Estado do jogo ---
player = criar_objeto((0, 1, 0), (1, 2, 1), ORANGE)

obstaculos = []
for _ in range(8):
    pos = (random.uniform(-10, 10), 1, random.uniform(-10, 10))
    tam = (random.uniform(1, 2), random.uniform(1, 3), random.uniform(1, 2))
    obstaculos.append(criar_objeto(pos, tam, AZURE))

velocidade   = 5
velocidade_y = 0.0
gravidade    = 20.0
no_chao      = True
keys_pressed = set()
ultimo_tempo = time.time()

# --- Janela ---
root   = tk.Tk()
root.title('Simulador de Hitbox 3D')
root.resizable(False, False)
canvas = tk.Canvas(root, width=SCREEN_W, height=SCREEN_H, bg=BG, highlightthickness=0)
canvas.pack()

root.bind('<KeyPress>',   lambda e: keys_pressed.add(e.keysym.lower()))
root.bind('<KeyRelease>', lambda e: keys_pressed.discard(e.keysym.lower()))
root.bind('<Escape>',     lambda e: root.destroy())

def loop():
    global velocidade_y, no_chao, ultimo_tempo

    agora        = time.time()
    dt           = min(agora - ultimo_tempo, 0.05)
    ultimo_tempo = agora

    # Movimento
    if 'w' in keys_pressed:
        player['z'] += velocidade * dt
    if 's' in keys_pressed:
        player['z'] -= velocidade * dt
    if 'a' in keys_pressed:
        player['x'] -= velocidade * dt
    if 'd' in keys_pressed:
        player['x'] += velocidade * dt

    if 'space' in keys_pressed and no_chao:
        velocidade_y = 8
        no_chao      = False

    # Gravidade
    velocidade_y -= gravidade * dt
    player['y']  += velocidade_y * dt
    if player['y'] <= 1:
        player['y']  = 1
        velocidade_y = 0
        no_chao      = True

    # Colisões
    player['colidindo'] = False
    for obj in obstaculos:
        if aabb_colide(player, obj):
            player['colidindo'] = True
            obj['colidindo']    = True
        else:
            obj['colidindo']    = False

    # Renderizar
    canvas.delete('all')

    # Chão
    passo = 2
    lim   = 14
    for xi in range(-lim, lim, passo):
        for zi in range(-lim, lim, passo):
            p1 = para_tela(xi,       0, zi)
            p2 = para_tela(xi+passo, 0, zi)
            p3 = para_tela(xi,       0, zi+passo)
            canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=DARK_GRID, width=1)
            canvas.create_line(p1[0], p1[1], p3[0], p3[1], fill=DARK_GRID, width=1)

    # Objetos ordenados por profundidade
    todos = obstaculos + [player]
    todos.sort(key=lambda o: -(o['x'] + o['z']))

    for obj in todos:
        folga    = 0.15
        cor_hb   = RED_HB if obj['colidindo'] else GREEN_HB
        verts    = vertices_caixa(obj['x'], obj['y'], obj['z'],
                                  obj['w'],       obj['h'],       obj['d'])
        verts_hb = vertices_caixa(obj['x'], obj['y'], obj['z'],
                                  obj['w']+folga, obj['h']+folga, obj['d']+folga)
        desenhar_caixa(canvas, verts,    obj['cor'], 2)
        desenhar_caixa(canvas, verts_hb, cor_hb,     1)

    # HUD
    status  = 'COLISAO' if player['colidindo'] else 'LIVRE'
    cor_hud = RED_HB    if player['colidindo'] else GREEN_HB
    canvas.create_text(20, 20, text=f'Status: {status}',
                       fill=cor_hud, font=('Arial', 18, 'bold'), anchor='w')
    canvas.create_text(20, 44, text='W A S D - mover  |  ESPACO - pular  |  ESC - sair',
                       fill=WHITE,  font=('Arial', 16), anchor='w')
    canvas.create_text(20, 68,
                       text=f'Posicao: ({player["x"]:.1f}, {player["y"]:.1f}, {player["z"]:.1f})',
                       fill=GRAY,   font=('Arial', 16), anchor='w')

    root.after(16, loop)

root.after(16, loop)
root.mainloop()
