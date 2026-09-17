from PIL import Image, ImageDraw
from pathlib import Path
import math

# ==========================================
# CONFIGURACAO
# ==========================================

imagem_original = Path(
    "a_wide_stylized_dark_themed_cinematic_develope.png"
)

pasta_saida = Path("assets")
pasta_saida.mkdir(exist_ok=True)

# ==========================================
# CARREGAR IMAGEM
# ==========================================

imagem = Image.open(imagem_original).convert("RGB")
largura, altura = imagem.size

# ==========================================
# CONFIGURACAO DOS FRAMES
# ==========================================

frames = []
quantidade_frames = 16
duracao = 120

# ==========================================
# GERAR ANIMACAO
# ==========================================

for i in range(quantidade_frames):
    t = i / (quantidade_frames - 1)

    # Movimento suave de zoom
    escala = 1.0 + 0.012 * math.sin(t * math.pi * 2)

    nova_largura = int(largura * escala)
    nova_altura = int(altura * escala)

    frame = imagem.resize(
        (nova_largura, nova_altura),
        Image.Resampling.LANCZOS,
    )

    # ======================================
    # MOVIMENTO DA CAMERA
    # ======================================

    esquerda = max(
        0,
        (nova_largura - largura) // 2
        + int(4 * math.sin(t * math.pi * 2)),
    )

    topo = max(
        0,
        (nova_altura - altura) // 2
        + int(3 * math.cos(t * math.pi * 2)),
    )

    frame = frame.crop(
        (esquerda, topo, esquerda + largura, topo + altura)
    )

    # ======================================
    # OVERLAY DA ANIMACAO
    # ======================================

    overlay = Image.new(
        "RGBA", (largura, altura), (0, 0, 0, 0)
    )
    desenho = ImageDraw.Draw(overlay)

    # Pulso
    pulso = (math.sin(t * math.pi * 2) + 1) / 2

    # ======================================
    # AREA DO COMPUTADOR
    # ======================================

    x0 = int(largura * 0.68)
    y0 = int(altura * 0.48)
    x1 = int(largura * 0.97)
    y1 = int(altura * 0.83)

    transparencia = int(18 + 28 * pulso)

    desenho.rounded_rectangle(
        (x0, y0, x1, y1),
        radius=18,
        outline=(70, 180, 255, transparencia),
        width=3,
    )

    # ======================================
    # CURSOR ANIMADO
    # ======================================

    cursor_x = int(largura * 0.80)
    cursor_y = int(
        altura * (0.76 + 0.015 * math.sin(t * math.pi * 2))
    )

    desenho.rectangle(
        (cursor_x, cursor_y, cursor_x + 5, cursor_y + 18),
        fill=(90, 220, 255, int(80 + 120 * pulso)),
    )

    # ======================================
    # JUNTAR CAMADAS
    # ======================================

    frame = Image.alpha_composite(
        frame.convert("RGBA"), overlay
    ).convert("RGB")

    frames.append(frame)

# ==========================================
# SALVAR GIF
# ==========================================

arquivo_gif = pasta_saida / "vitor-coding.gif"

frames[0].save(
    arquivo_gif,
    save_all=True,
    append_images=frames[1:],
    duration=duracao,
    loop=0,
    optimize=True,
)

print(f"GIF criado em: {arquivo_gif}")
