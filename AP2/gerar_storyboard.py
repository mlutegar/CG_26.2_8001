"""Gera AP2/storyboard/AP2_storyboard.png (6 quadros) e AP2/saida/comparacao_motor.png.
Uso: python AP2/gerar_storyboard.py  (precisa de AP2/saida/frames/, gerado no render final)."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(BASE, "saida", "frames")
QUADROS = [
    (1, "Início", "Cena estabelecida; blocos ainda fora do quadro, prestes a cair; palavra oculta.", "Plano geral aberto, câmera baixa (y -21)"),
    (72, "Início", "Blocos assentados; câmera aproxima (push-in).", "Plano geral, câmera avançando"),
    (140, "Desenvolvimento", "Ibmec sobe e cresce; tela do computador acende; robô olha a tela.", "Plano de conjunto"),
    (214, "Desenvolvimento", "Ponto do i encaixado, pulso final; robô vira para a câmera.", "Plano de conjunto, Ibmec centralizada"),
    (300, "Encerramento", "Foguete decola com chama; robô acena.", "Plano de conjunto, quase travado"),
    (360, "Encerramento", "Hero shot: Ibmec legível, foguete no terço superior direito.", "Plano de conjunto travado (y -14.2)"),
]
def fonte(t):
    for p in (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\segoeui.ttf"):
        if os.path.isfile(p):
            return ImageFont.truetype(p, t)
    return ImageFont.load_default()
def quebra(d, txt, f, larg):
    linhas, atual = [], ""
    for p in txt.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) <= larg: atual = t
        else: linhas.append(atual); atual = p
    return linhas + [atual]
W, H, M, CAPH = 640, 360, 16, 120
f1, f2 = fonte(19), fonte(16)
img = Image.new("RGB", (3 * W + 4 * M, 2 * (H + CAPH) + 3 * M + 50), (245, 245, 245))
d = ImageDraw.Draw(img)
d.text((M, 12), "AP2 · Storyboard atualizado · 360 frames @ 24 fps (15 s)", font=fonte(22), fill=(20, 40, 90))
for i, (fr, mom, acao, enq) in enumerate(QUADROS):
    x = M + (i % 3) * (W + M); y = 50 + M + (i // 3) * (H + CAPH + M)
    im = Image.open(os.path.join(FR, f"f_{fr:04d}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
    img.paste(im, (x, y)); d.rectangle([x, y, x + W, y + H + CAPH], outline=(20, 40, 90), width=2)
    d.text((x + 8, y + H + 6), f"Quadro {i+1} · frame {fr} ({(fr-1)/24:.1f} s) · {mom}", font=f1, fill=(20, 40, 90))
    yy = y + H + 32
    for l in quebra(d, "Ação: " + acao, f2, W - 16) + quebra(d, "Enquadramento: " + enq, f2, W - 16):
        d.text((x + 8, yy), l, font=f2, fill=(30, 30, 30)); yy += 20
os.makedirs(os.path.join(BASE, "storyboard"), exist_ok=True)
img.save(os.path.join(BASE, "storyboard", "AP2_storyboard.png"))
# comparacao de motor (frame 300)
TM = os.path.join(BASE, "saida", "teste_motor")
a = Image.open(os.path.join(TM, "eevee_next_f300.png")).convert("RGB").resize((960, 540), Image.LANCZOS)
b = Image.open(os.path.join(TM, "cycles_optix_64spp_f300.png")).convert("RGB").resize((960, 540), Image.LANCZOS)
c = Image.new("RGB", (1920 + 30, 540 + 50), (245, 245, 245)); c.paste(a, (10, 40)); c.paste(b, (980, 40))
dd = ImageDraw.Draw(c); ft = fonte(22)
dd.text((10, 8), "Eevee Next (1,5 s/frame) · frame 300", font=ft, fill=(20, 40, 90))
dd.text((980, 8), "Cycles OptiX 64 spp (6,5 s/frame) · frame 300", font=ft, fill=(20, 40, 90))
c.save(os.path.join(BASE, "saida", "comparacao_motor.png"))
print("ok")
