from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

# ==========================================
# DADOS DE CONTRIBUICAO (seu GitHub)
# ==========================================

# Grade 7x52 (semanas x dias da semana)
# Cada tupla: (semana, dia_semana, contribuicoes)
contribuicoes_raw = [
    (16, 5, 2),   # 28 Dez
    (35, 1, 2),   # 24 Ago
    (38, 4, 4),   # 17 Set (hoje)
]

# ==========================================
# CONFIGURACAO DA ANIMACAO
# ==========================================

CELL_SIZE = 12
CELL_GAP = 3
GRID_COLS = 52
GRID_ROWS = 7
MARGIN_LEFT = 60
MARGIN_TOP = 40
SNAKE_SIZE = CELL_SIZE

BG_COLOR = (13, 17, 23)
EMPTY_COLOR = (22, 27, 34)
COMMIT_COLORS = {
    0: (22, 27, 34),
    1: (14, 68, 41),
    2: (0, 109, 50),
    3: (38, 166, 65),
    4: (57, 211, 83),
}
SNAKE_HEAD_COLOR = (57, 211, 83)
SNAKE_BODY_COLOR = (38, 166, 65)
TEXT_COLOR = (139, 148, 158)
EATEN_COLOR = (57, 211, 83)

FRAME_WIDTH = MARGIN_LEFT + GRID_COLS * (CELL_SIZE + CELL_GAP) + 20
FRAME_HEIGHT = MARGIN_TOP + GRID_ROWS * (CELL_SIZE + CELL_GAP) + 60

# ==========================================
# GERAR GRADE
# ==========================================

grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
commit_positions = []

for semana, dia, contrib in contribuicoes_raw:
    if 0 <= semana < GRID_COLS and 0 <= dia < GRID_ROWS:
        grid[dia][semana] = contrib
        commit_positions.append((semana, dia, contrib))

commit_positions.sort(key=lambda x: (x[0], x[1]))

# ==========================================
# ENCONTRAR CAMINHO DA COBRA
# ==========================================

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def build_path(commits):
    if not commits:
        return []

    path = []
    start = (-1, 3)
    path.append(start)

    remaining = list(commits)
    current = start

    while remaining:
        nearest = min(remaining, key=lambda c: manhattan_distance(current, c[:2]))
        target = (nearest[0], nearest[1])

        x, y = current
        tx, ty = target

        while x != tx:
            x += 1 if tx > x else -1
            path.append((x, y))
        while y != ty:
            y += 1 if ty > y else -1
            path.append((x, y))

        current = target
        remaining.remove(nearest)

    return path

snake_path = build_path(commit_positions)

# ==========================================
# CRIAR FRAMES
# ==========================================

def draw_grid(draw, eaten_cells):
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = MARGIN_LEFT + col * (CELL_SIZE + CELL_GAP)
            y = MARGIN_TOP + row * (CELL_SIZE + CELL_GAP)

            if (col, row) in eaten_cells:
                color = EATEN_COLOR
            elif grid[row][col] > 0:
                color = COMMIT_COLORS[min(grid[row][col], 4)]
            else:
                color = EMPTY_COLOR

            draw.rounded_rectangle(
                (x, y, x + CELL_SIZE, y + CELL_SIZE),
                radius=2,
                fill=color,
            )

def draw_month_labels(draw):
    months = [
        (1, "Jan"), (5, "Fev"), (9, "Mar"), (13, "Abr"),
        (17, "Mai"), (22, "Jun"), (26, "Jul"), (30, "Ago"),
        (35, "Set"), (39, "Out"), (43, "Nov"), (47, "Dez"),
    ]
    for week, label in months:
        x = MARGIN_LEFT + week * (CELL_SIZE + CELL_GAP)
        draw.text((x, MARGIN_TOP - 16), label, fill=TEXT_COLOR)

def draw_day_labels(draw):
    days = ["", "Seg", "", "Qua", "", "Sex", ""]
    for i, day in enumerate(days):
        if day:
            y = MARGIN_TOP + i * (CELL_SIZE + CELL_GAP)
            draw.text((5, y), day, fill=TEXT_COLOR)

def draw_snake(draw, path_pos, length=6):
    start_idx = max(0, path_pos - length + 1)
    body = snake_path[start_idx:path_pos + 1]

    for i in range(len(body) - 1):
        x = MARGIN_LEFT + body[i][0] * (CELL_SIZE + CELL_GAP)
        y = MARGIN_TOP + body[i][1] * (CELL_SIZE + CELL_GAP)
        draw.rounded_rectangle(
            (x - 1, y - 1, x + CELL_SIZE + 1, y + CELL_SIZE + 1),
            radius=3,
            fill=SNAKE_BODY_COLOR,
        )

    if body:
        hx = MARGIN_LEFT + body[-1][0] * (CELL_SIZE + CELL_GAP)
        hy = MARGIN_TOP + body[-1][1] * (CELL_SIZE + CELL_GAP)
        draw.rounded_rectangle(
            (hx - 2, hy - 2, hx + CELL_SIZE + 2, hy + CELL_SIZE + 2),
            radius=4,
            fill=SNAKE_HEAD_COLOR,
        )
        draw.ellipse(
            (hx + 2, hy + 2, hx + 5, hy + 5),
            fill=BG_COLOR,
        )

def draw_title(draw, frame_idx, total_frames, eaten):
    title = "COBA COMENDO COMMITS"
    draw.text((MARGIN_LEFT, FRAME_HEIGHT - 40), title, fill=TEXT_COLOR)

    eaten_count = len([e for e in eaten if e in [(c[0], c[1]) for c in commit_positions]])
    stats = f"Commits: {eaten_count}/{len(commit_positions)}"
    draw.text((MARGIN_LEFT, FRAME_HEIGHT - 22), stats, fill=SNAKE_HEAD_COLOR)

# ==========================================
# GERAR ANIMACAO
# ==========================================

frames = []
total_steps = len(snake_path)
pause_frames = 15

commit_set = set((c[0], c[1]) for c in commit_positions)
eaten_cells = set()

for step in range(total_steps):
    img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    pos = snake_path[step]
    if pos in commit_set:
        eaten_cells.add(pos)

    draw_grid(draw, eaten_cells)
    draw_month_labels(draw)
    draw_day_labels(draw)
    draw_snake(draw, step, length=7)
    draw_title(draw, step, total_steps, eaten_cells)

    frames.append(img)

for _ in range(pause_frames):
    img = Image.new("RGB", (FRAME_WIDTH, FRAME_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    draw_grid(draw, eaten_cells)
    draw_month_labels(draw)
    draw_day_labels(draw)
    draw_snake(draw, total_steps - 1, length=7)
    draw_title(draw, total_steps, total_steps, eaten_cells)

    frames.append(img)

# ==========================================
# SALVAR GIF
# ==========================================

pasta_saida = Path("assets")
pasta_saida.mkdir(exist_ok=True)
arquivo_gif = pasta_saida / "snake-eating-commits.gif"

frames[0].save(
    arquivo_gif,
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True,
)

print(f"GIF criado em: {arquivo_gif}")
print(f"Total de frames: {len(frames)}")
print(f"Commits encontrados: {len(commit_positions)}")
