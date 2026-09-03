"""
AC01 - Computacao Visual | Area 1: SINTESE DE IMAGENS (Computacao Grafica)

Entrada: descricao matematica de uma cena 3D (esferas, materiais, camera).
Saida:   uma imagem raster.

Ray tracer de Monte Carlo escrito com numpy vetorizado (sem GPU, sem
dependencia externa alem de numpy/matplotlib). A implementacao segue o
roteiro classico do livro "Ray Tracing in One Weekend" (Peter Shirley),
traduzido para operacoes de array para rodar em tempo aceitavel em CPU.

Aspectos especificos da area demonstrados aqui:
  1. A cena e' um MODELO (dados geometricos), nao uma imagem.
  2. Modelo de camera pinhole: geracao de raios primarios por pixel.
  3. Modelos de material / BRDF: lambertiano (difuso) e metalico (especular).
  4. Iluminacao global por Monte Carlo: a cor de um pixel e' uma INTEGRAL
     estimada por amostragem aleatoria.
  5. Anti-aliasing por supersampling (jitter dentro do pixel).
  6. Textura procedural (xadrez) avaliada no ponto de intersecao.
  7. Correcao gama na conversao de radiancia linear -> valor de pixel sRGB.
  8. Custo computacional cresce linearmente com o numero de amostras (spp).

Execucao:
    python raytracer.py
"""

import json
import os
import time

import numpy as np

RNG = np.random.default_rng(42)
AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")

# --------------------------------------------------------------------------
# 1. DESCRICAO DA CENA  (a "entrada" da sintese de imagens)
# --------------------------------------------------------------------------
# Cada esfera: centro, raio, albedo (cor), tipo de material e rugosidade.
CENA = [
    {"centro": [0.0, -100.5, -1.0], "raio": 100.0, "albedo": [0.62, 0.62, 0.58],
     "material": "lambertiano", "fuzz": 0.0, "nome": "chao",
     "textura": "xadrez", "albedo2": [0.18, 0.20, 0.24], "escala_textura": 1.6},
    {"centro": [0.0, 0.0, -1.2], "raio": 0.5, "albedo": [0.80, 0.25, 0.25],
     "material": "lambertiano", "fuzz": 0.0, "nome": "esfera_vermelha"},
    {"centro": [-1.05, 0.0, -1.2], "raio": 0.5, "albedo": [0.80, 0.80, 0.85],
     "material": "metal", "fuzz": 0.02, "nome": "esfera_metal"},
    {"centro": [1.05, 0.0, -1.2], "raio": 0.5, "albedo": [0.85, 0.65, 0.25],
     "material": "metal", "fuzz": 0.35, "nome": "esfera_ouro_fosco"},
]

CAMERA = {
    "origem": [0.0, 0.35, 1.35],
    "alvo": [0.0, 0.0, -1.2],
    "vup": [0.0, 1.0, 0.0],
    "vfov_graus": 58.0,
}

LARGURA, ALTURA = 480, 270
PROFUNDIDADE_MAX = 8


# --------------------------------------------------------------------------
# 2. UTILITARIOS VETORIAIS
# --------------------------------------------------------------------------
def normalizar(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def direcoes_aleatorias(n):
    """Amostra n direcoes uniformes sobre a esfera unitaria."""
    v = RNG.normal(size=(n, 3))
    return normalizar(v)


# --------------------------------------------------------------------------
# 3. CAMERA PINHOLE: transforma pixels em raios primarios
# --------------------------------------------------------------------------
def construir_camera(cam, largura, altura):
    origem = np.array(cam["origem"], dtype=np.float64)
    alvo = np.array(cam["alvo"], dtype=np.float64)
    vup = np.array(cam["vup"], dtype=np.float64)

    theta = np.deg2rad(cam["vfov_graus"])
    altura_vp = 2.0 * np.tan(theta / 2.0)
    largura_vp = altura_vp * (largura / altura)

    w = normalizar(origem - alvo)          # eixo optico (aponta para tras)
    u = normalizar(np.cross(vup, w))       # direita
    v = np.cross(w, u)                     # cima

    horizontal = largura_vp * u
    vertical = altura_vp * v
    canto_inferior_esq = origem - horizontal / 2 - vertical / 2 - w
    return origem, horizontal, vertical, canto_inferior_esq


def gerar_raios(cam_params, largura, altura, jitter=True):
    origem, horizontal, vertical, canto = cam_params
    jx = RNG.random((altura, largura)) if jitter else np.full((altura, largura), 0.5)
    jy = RNG.random((altura, largura)) if jitter else np.full((altura, largura), 0.5)

    ix = (np.arange(largura)[None, :] + jx) / largura
    iy = (np.arange(altura)[:, None] + jy) / altura
    iy = 1.0 - iy  # imagem cresce para baixo, viewport cresce para cima

    alvo = (canto[None, None, :]
            + ix[..., None] * horizontal[None, None, :]
            + iy[..., None] * vertical[None, None, :])
    direcoes = normalizar(alvo - origem[None, None, :]).reshape(-1, 3)
    origens = np.repeat(origem[None, :], direcoes.shape[0], axis=0)
    return origens, direcoes


# --------------------------------------------------------------------------
# 4. INTERSECAO RAIO-ESFERA (resolvida para todos os raios de uma vez)
# --------------------------------------------------------------------------
def intersectar(origens, direcoes, cena, t_min=1e-3, t_max=1e9):
    n = origens.shape[0]
    t_melhor = np.full(n, np.inf)
    idx_melhor = np.full(n, -1, dtype=np.int32)

    for i, esfera in enumerate(cena):
        c = np.asarray(esfera["centro"])
        r = esfera["raio"]
        oc = origens - c
        b = np.einsum("ij,ij->i", oc, direcoes)      # direcoes normalizadas => a = 1
        c_term = np.einsum("ij,ij->i", oc, oc) - r * r
        disc = b * b - c_term

        ok = disc > 0
        if not ok.any():
            continue
        sq = np.sqrt(np.where(ok, disc, 0.0))
        t1 = -b - sq
        t2 = -b + sq
        t = np.where((t1 > t_min) & (t1 < t_max), t1, t2)
        valido = ok & (t > t_min) & (t < t_max) & (t < t_melhor)
        t_melhor = np.where(valido, t, t_melhor)
        idx_melhor = np.where(valido, i, idx_melhor)

    return t_melhor, idx_melhor


def ceu(direcoes):
    """Luz ambiente: gradiente vertical (modelo de iluminacao mais simples)."""
    t = 0.5 * (direcoes[:, 1] + 1.0)
    branco = np.array([1.0, 1.0, 1.0])
    azul = np.array([0.5, 0.7, 1.0])
    return (1.0 - t)[:, None] * branco + t[:, None] * azul


# --------------------------------------------------------------------------
# 5. NUCLEO DO PATH TRACER
# --------------------------------------------------------------------------
def tracar(origens, direcoes, cena, profundidade_max=PROFUNDIDADE_MAX):
    n = origens.shape[0]
    cor = np.zeros((n, 3))
    throughput = np.ones((n, 3))
    ativo = np.ones(n, dtype=bool)

    albedos = np.array([e["albedo"] for e in cena])
    albedos2 = np.array([e.get("albedo2", e["albedo"]) for e in cena])
    texturizada = np.array([e.get("textura") == "xadrez" for e in cena])
    escala_tex = np.array([e.get("escala_textura", 1.0) for e in cena])
    metal = np.array([e["material"] == "metal" for e in cena])
    fuzz = np.array([e["fuzz"] for e in cena])
    centros = np.array([e["centro"] for e in cena])
    raios = np.array([e["raio"] for e in cena])

    for _ in range(profundidade_max):
        if not ativo.any():
            break
        o = origens[ativo]
        d = direcoes[ativo]
        t, idx = intersectar(o, d, cena)

        acertou = idx >= 0
        # Raios que escaparam da cena colhem a cor do ceu e sao encerrados.
        globais = np.where(ativo)[0]
        escapou = globais[~acertou]
        if escapou.size:
            cor[escapou] += throughput[escapou] * ceu(direcoes[escapou])
            ativo[escapou] = False

        if not acertou.any():
            continue

        gi = globais[acertou]
        o_h, d_h, t_h, id_h = o[acertou], d[acertou], t[acertou], idx[acertou]

        p = o_h + t_h[:, None] * d_h
        nrm = normalizar(p - centros[id_h])
        # Garante normal apontando contra o raio incidente.
        frente = np.einsum("ij,ij->i", d_h, nrm) < 0
        nrm = np.where(frente[:, None], nrm, -nrm)

        eh_metal = metal[id_h]
        # Espalhamento lambertiano: normal + direcao aleatoria na esfera unitaria
        d_dif = normalizar(nrm + direcoes_aleatorias(nrm.shape[0]) * 0.999)
        # Reflexao especular com rugosidade (fuzz)
        d_esp = d_h - 2.0 * np.einsum("ij,ij->i", d_h, nrm)[:, None] * nrm
        d_esp = normalizar(d_esp + fuzz[id_h][:, None] * direcoes_aleatorias(nrm.shape[0]))

        nova_dir = np.where(eh_metal[:, None], d_esp, d_dif)

        # Textura procedural: o albedo passa a depender do PONTO da superficie
        cor_base = albedos[id_h]
        tex = texturizada[id_h]
        if tex.any():
            k = escala_tex[id_h][:, None]
            xadrez = ((np.floor(p[:, 0:1] * k) + np.floor(p[:, 2:3] * k))
                      % 2 == 0)
            cor_base = np.where(tex[:, None],
                                np.where(xadrez, albedos[id_h], albedos2[id_h]),
                                cor_base)
        throughput[gi] *= cor_base
        origens[gi] = p + 1e-4 * nrm
        direcoes[gi] = nova_dir

        # Metal que reflete para dentro da superficie: raio morre.
        morto = eh_metal & (np.einsum("ij,ij->i", nova_dir, nrm) <= 0)
        ativo[gi[morto]] = False

    return cor


def renderizar(largura, altura, spp, cena=CENA, cam=CAMERA):
    cam_params = construir_camera(cam, largura, altura)
    acumulado = np.zeros((altura * largura, 3))
    for _ in range(spp):
        o, d = gerar_raios(cam_params, largura, altura, jitter=(spp > 1))
        acumulado += tracar(o, d, cena)
    return (acumulado / spp).reshape(altura, largura, 3)


def para_srgb(img_linear):
    """Correcao gama 2.2 + quantizacao para 8 bits."""
    img = np.clip(img_linear, 0.0, 1.0) ** (1.0 / 2.2)
    return (img * 255.0 + 0.5).astype(np.uint8)


# --------------------------------------------------------------------------
# 6. PROJECAO DA CENA (usada depois pela area 3, Visao Computacional)
# --------------------------------------------------------------------------
def projetar_esferas(cena, cam, largura, altura):
    """Projeta o centro/raio de cada esfera para coordenadas de pixel.

    Esse arquivo e' o 'gabarito': a area de Visao Computacional vai tentar
    RECUPERAR esses numeros olhando apenas para a imagem renderizada.
    """
    origem, horizontal, vertical, canto = construir_camera(cam, largura, altura)
    w = normalizar(np.array(cam["origem"]) - np.array(cam["alvo"]))
    u = normalizar(np.cross(np.array(cam["vup"]), w))
    v = np.cross(w, u)
    theta = np.deg2rad(cam["vfov_graus"])
    h_vp = 2.0 * np.tan(theta / 2.0)
    w_vp = h_vp * (largura / altura)

    resultado = []
    for e in cena:
        if e["raio"] > 10:      # o "chao" e' uma esfera gigante, nao interessa
            continue
        c = np.asarray(e["centro"]) - origem
        z = -float(np.dot(c, w))     # profundidade ao longo do eixo optico
        if z <= 0:
            continue
        x = float(np.dot(c, u))
        y = float(np.dot(c, v))
        px = (x / z / (w_vp / 2.0) * 0.5 + 0.5) * largura
        py = (1.0 - (y / z / (h_vp / 2.0) * 0.5 + 0.5)) * altura
        praio = (e["raio"] / z / (h_vp / 2.0) * 0.5) * altura
        resultado.append({"nome": e["nome"], "cx": round(px, 1),
                          "cy": round(py, 1), "raio_px": round(praio, 1),
                          "material": e["material"]})
    return resultado


# --------------------------------------------------------------------------
# 7. MAIN
# --------------------------------------------------------------------------
def main():
    os.makedirs(SAIDA, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image

    print("=" * 68)
    print("AREA 1 - SINTESE DE IMAGENS  (cena 3D  ->  imagem)")
    print("=" * 68)
    print(f"Cena: {len(CENA)} esferas | Resolucao: {LARGURA}x{ALTURA} "
          f"| Profundidade max: {PROFUNDIDADE_MAX}")

    # Experimento 1: efeito do numero de amostras por pixel (spp)
    amostras = [1, 4, 16, 64]
    imagens, tempos = [], []
    for spp in amostras:
        t0 = time.time()
        img = renderizar(LARGURA, ALTURA, spp)
        dt = time.time() - t0
        imagens.append(para_srgb(img))
        tempos.append(dt)
        print(f"  spp={spp:>3}  tempo={dt:6.2f}s  "
              f"({dt / max(tempos[0], 1e-9):5.1f}x o custo de 1 spp)")
        Image.fromarray(imagens[-1]).save(
            os.path.join(SAIDA, f"render_{spp:03d}spp.png"))

    # Figura comparativa: ruido de Monte Carlo x custo
    fig, eixos = plt.subplots(2, 2, figsize=(11, 6.2))
    for ax, img, spp, dt in zip(eixos.ravel(), imagens, amostras, tempos):
        ax.imshow(img)
        ax.set_title(f"{spp} amostras/pixel  -  {dt:.2f}s", fontsize=10)
        ax.axis("off")
    fig.suptitle("Sintese de imagens: convergencia de Monte Carlo e "
                 "anti-aliasing", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "comparacao_amostragem.png"), dpi=110)
    plt.close(fig)

    # Recorte ampliado mostrando serrilhado (aliasing) em 1 spp
    rec = (slice(int(ALTURA * 0.38), int(ALTURA * 0.62)),
           slice(int(LARGURA * 0.24), int(LARGURA * 0.48)))
    fig, eixos = plt.subplots(1, 2, figsize=(9, 3.4))
    for ax, img, tit in zip(eixos, [imagens[0][rec], imagens[-1][rec]],
                            ["1 amostra/pixel (serrilhado + ruido)",
                             "64 amostras/pixel (anti-aliasing)"]):
        ax.imshow(img, interpolation="nearest")
        ax.set_title(tit, fontsize=10)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "detalhe_aliasing.png"), dpi=130)
    plt.close(fig)

    # Imagem de referencia usada pelas areas 2 e 3
    ref = para_srgb(renderizar(LARGURA, ALTURA, 96))
    Image.fromarray(ref).save(os.path.join(SAIDA, "render_referencia.png"))

    # Gabarito geometrico para a area de Visao Computacional
    gabarito = {
        "resolucao": [LARGURA, ALTURA],
        "camera": CAMERA,
        "esferas_projetadas": projetar_esferas(CENA, CAMERA, LARGURA, ALTURA),
    }
    with open(os.path.join(SAIDA, "cena_gabarito.json"), "w") as f:
        json.dump(gabarito, f, indent=2, ensure_ascii=False)

    print("\nArquivos gerados em 01_sintese_imagens/saida/:")
    for nome in sorted(os.listdir(SAIDA)):
        print("  -", nome)
    print("\nObservacao para o relatorio: o tempo cresce de forma "
          "aproximadamente linear\ncom spp, enquanto o ruido cai com "
          "1/sqrt(spp). Esse e' o compromisso central\nda sintese por "
          "Monte Carlo.")


if __name__ == "__main__":
    main()
