"""
AC01 - Computacao Visual | Area 4: VISUALIZACAO COMPUTACIONAL

Entrada: DADOS abstratos, sem forma visual propria (aqui, um campo escalar
         3D produzido por uma simulacao de difusao - o analogo de um exame
         de tomografia ou de uma simulacao de fluidos).
Saida:   uma imagem.

A diferenca para a Area 1 e' o que a imagem representa. Na sintese existe
uma resposta fisicamente correta: a imagem que a camera veria. Aqui nao.
O dado nao tem cor nem opacidade; quem as atribui e' o projetista, atraves
do MAPEAMENTO VISUAL. O mesmo volume gera imagens completamente diferentes
conforme a funcao de transferencia escolhida - e e' exatamente isso que
este programa demonstra.

Aspectos especificos da area demonstrados aqui:
  1. Dado abstrato -> geometria: o volume nao "e'" um objeto 3D, virou um.
  2. Fatiamento ortogonal (a visualizacao mais elementar de um volume).
  3. Mapas de cores e percepcao: por que arco-iris/jet distorce a leitura
     (perfil de luminancia nao monotonico) e viridis nao.
  4. Funcao de transferencia (valor -> cor + opacidade) como decisao de
     projeto: tres TFs, tres imagens, o mesmo dado.
  5. Extracao de isosuperficies com marching cubes.
  6. Volume rendering por composicao alfa front-to-back (ray casting).

Execucao:
    python visualizacao.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from skimage import measure

def paleta(nome):
    """Compatibilidade entre versoes do matplotlib (cm.get_cmap foi removido)."""
    try:
        return matplotlib.colormaps[nome]
    except (AttributeError, KeyError):
        from matplotlib import cm
        return cm.get_cmap(nome)


AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
N = 96


# --------------------------------------------------------------------------
# 1. O DADO: um campo escalar 3D vindo de uma "simulacao"
# --------------------------------------------------------------------------
def gerar_volume(n=N, semente=11):
    """Difusao a partir de fontes pontuais + turbulencia de fundo.

    Nao ha nada de visual aqui: e' apenas um array (n, n, n) de floats,
    como sairia de um simulador de CFD ou de um tomografo.
    """
    rng = np.random.default_rng(semente)
    vol = np.zeros((n, n, n), dtype=np.float32)

    fontes = [(0.35, 0.40, 0.45, 1.00, 6.0),
              (0.65, 0.60, 0.55, 0.85, 9.0),
              (0.50, 0.30, 0.70, 0.60, 4.0)]
    z, y, x = np.mgrid[0:n, 0:n, 0:n].astype(np.float32) / n
    for cz, cy, cx, amp, k in fontes:
        d2 = (z - cz) ** 2 + (y - cy) ** 2 + (x - cx) ** 2
        vol += amp * np.exp(-k * d2 * 12.0)

    # Estrutura filamentar (correlacao espacial), como turbulencia
    ruido = ndimage.gaussian_filter(rng.normal(size=(n, n, n)), sigma=3.0)
    ruido /= np.abs(ruido).max()
    vol += 0.35 * ruido

    # Alguns passos de difusao explicita
    for _ in range(3):
        vol = ndimage.gaussian_filter(vol, sigma=0.9)

    vol -= vol.min()
    vol /= vol.max()
    return vol.astype(np.float32)


# --------------------------------------------------------------------------
# 2. FATIAMENTO ORTOGONAL
# --------------------------------------------------------------------------
def fig_fatias(vol):
    n = vol.shape[0]
    cortes = [(vol[n // 2, :, :], "corte axial (z = n/2)"),
              (vol[:, n // 2, :], "corte coronal (y = n/2)"),
              (vol[:, :, n // 2], "corte sagital (x = n/2)")]
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.6))
    for a, (im, tit) in zip(ax, cortes):
        m = a.imshow(im, cmap="viridis", vmin=0, vmax=1)
        a.set_title(tit, fontsize=10)
        a.axis("off")
    ax[3].hist(vol.ravel(), bins=120, color="#1D9E75")
    ax[3].set_title("histograma do campo escalar", fontsize=10)
    ax[3].set_xlabel("valor")
    ax[3].set_yticks([])
    fig.suptitle("Visualizacao 1: fatiamento - o dado 3D reduzido a "
                 "imagens 2D", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "01_fatias_ortogonais.png"), dpi=110)
    plt.close(fig)


# --------------------------------------------------------------------------
# 3. MAPAS DE CORES E PERCEPCAO
# --------------------------------------------------------------------------
def _luminancia(nome):
    cores = paleta(nome)(np.linspace(0, 1, 256))[:, :3]
    # Luminancia relativa (Rec. 709)
    return 0.2126 * cores[:, 0] + 0.7152 * cores[:, 1] + 0.0722 * cores[:, 2]


def fig_colormaps(vol):
    fatia = vol[vol.shape[0] // 2]
    mapas = ["gray", "jet", "viridis"]
    fig, ax = plt.subplots(2, 3, figsize=(12, 6.4),
                           gridspec_kw={"height_ratios": [3, 1]})
    for j, nome in enumerate(mapas):
        ax[0, j].imshow(fatia, cmap=nome, vmin=0, vmax=1)
        ax[0, j].set_title(f"mapa de cores: {nome}", fontsize=10)
        ax[0, j].axis("off")
        lum = _luminancia(nome)
        mono = "monotonica" if np.all(np.diff(lum) > -1e-3) else "NAO monotonica"
        ax[1, j].plot(np.linspace(0, 1, 256), lum, color="#534AB7")
        ax[1, j].set_title(f"luminancia: {mono}", fontsize=9)
        ax[1, j].set_ylim(0, 1)
        ax[1, j].set_xlabel("valor do dado")
    fig.suptitle("O mesmo dado, tres leituras: jet cria fronteiras que nao "
                 "existem no campo", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "02_mapas_de_cores.png"), dpi=110)
    plt.close(fig)


# --------------------------------------------------------------------------
# 4. FUNCAO DE TRANSFERENCIA + VOLUME RENDERING (ray casting)
# --------------------------------------------------------------------------
def funcao_transferencia(valores, tipo):
    """valor escalar -> (cor RGB, opacidade). ESTA e' a decisao de projeto."""
    v = np.clip(valores, 0, 1)
    if tipo == "rampa":
        # Opacidade cresce linearmente: tudo aparece, nada se destaca
        alpha = 0.055 * v ** 2
        rgb = paleta("viridis")(v)[..., :3]
    elif tipo == "isolar_nucleo":
        # Janela estreita em torno dos valores altos: destaca as fontes
        alpha = 0.16 * np.exp(-((v - 0.86) ** 2) / (2 * 0.045 ** 2))
        rgb = paleta("inferno")(v)[..., :3]
    elif tipo == "duas_camadas":
        # Duas janelas: "casca" semitransparente + "nucleo" opaco
        a1 = 0.020 * np.exp(-((v - 0.55) ** 2) / (2 * 0.060 ** 2))
        a2 = 0.150 * np.exp(-((v - 0.88) ** 2) / (2 * 0.035 ** 2))
        alpha = a1 + a2
        rgb = np.zeros(v.shape + (3,))
        casca = np.array([0.20, 0.55, 0.85])
        nucleo = np.array([0.95, 0.75, 0.25])
        peso = (a2 / (a1 + a2 + 1e-9))[..., None]
        rgb = (1 - peso) * casca + peso * nucleo
    else:
        raise ValueError(tipo)
    return rgb, alpha


def volume_rendering(vol, tipo, eixo=1):
    """Composicao alfa front-to-back ao longo de um eixo.

    E' o mesmo ray casting da Area 1, mas a 'materia' que o raio atravessa
    nao veio da fisica: veio da funcao de transferencia escolhida.
    """
    v = np.moveaxis(vol, eixo, 0)
    saida = np.zeros(v.shape[1:] + (3,))
    transmitancia = np.ones(v.shape[1:])
    for k in range(v.shape[0]):
        rgb, alpha = funcao_transferencia(v[k], tipo)
        contrib = (alpha * transmitancia)[..., None]
        saida += contrib * rgb
        transmitancia *= (1.0 - alpha)
    fundo = 1.0
    saida += transmitancia[..., None] * fundo
    return np.clip(saida, 0, 1)


def fig_transferencia(vol):
    tipos = [("rampa", "TF rampa: opacidade ~ valor"),
             ("isolar_nucleo", "TF janela estreita: isola as fontes"),
             ("duas_camadas", "TF duas janelas: casca + nucleo")]
    fig, ax = plt.subplots(2, 3, figsize=(13, 7),
                           gridspec_kw={"height_ratios": [3, 1.1]})
    grade = np.linspace(0, 1, 256)
    for j, (tipo, tit) in enumerate(tipos):
        ax[0, j].imshow(volume_rendering(vol, tipo))
        ax[0, j].set_title(tit, fontsize=10)
        ax[0, j].axis("off")
        rgb, alpha = funcao_transferencia(grade, tipo)
        ax[1, j].plot(grade, alpha, color="#993C1D")
        ax[1, j].fill_between(grade, alpha, color="#F0997B", alpha=0.4)
        ax[1, j].set_title("opacidade atribuida ao valor", fontsize=9)
        ax[1, j].set_xlabel("valor do dado")
        ax[1, j].set_yticks([])
    fig.suptitle("Ponto central da area: MESMO volume, tres funcoes de "
                 "transferencia, tres imagens", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "03_funcoes_de_transferencia.png"), dpi=110)
    plt.close(fig)


# --------------------------------------------------------------------------
# 5. ISOSUPERFICIES (marching cubes)
# --------------------------------------------------------------------------
def fig_isosuperficies(vol):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    isovalores = [0.45, 0.65, 0.85]
    cores = ["#85B7EB", "#5DCAA5", "#EF9F27"]
    fig = plt.figure(figsize=(13, 4.8))
    contagens = []
    malhas = [measure.marching_cubes(vol, level=iso) for iso in isovalores]
    # Mesma caixa de visualizacao nos tres paineis, para poder comparar
    todos = np.vstack([m[0] for m in malhas])
    lo, hi = todos.min(axis=0) - 4, todos.max(axis=0) + 4
    for i, (iso, cor, (verts, faces, _, _)) in enumerate(
            zip(isovalores, cores, malhas), start=1):
        contagens.append((iso, len(verts), len(faces)))
        ax = fig.add_subplot(1, 3, i, projection="3d")
        malha = Poly3DCollection(verts[faces], alpha=0.9)
        malha.set_facecolor(cor)
        malha.set_edgecolor("none")
        ax.add_collection3d(malha)
        ax.set_xlim(lo[0], hi[0]); ax.set_ylim(lo[1], hi[1])
        ax.set_zlim(lo[2], hi[2])
        ax.set_box_aspect((1, 1, 1))
        ax.set_title(f"isovalor = {iso}\n{len(faces)} triangulos", fontsize=10,
                     pad=2)
        ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
        ax.view_init(elev=22, azim=38)
    fig.suptitle("Marching cubes: o dado abstrato ganha GEOMETRIA - e a "
                 "partir daqui vira computacao grafica", fontsize=12, y=0.99)
    fig.subplots_adjust(top=0.80, bottom=0.02, left=0.02, right=0.98)
    fig.savefig(os.path.join(SAIDA, "04_isosuperficies.png"), dpi=110)
    plt.close(fig)
    return contagens


def main():
    os.makedirs(SAIDA, exist_ok=True)
    print("=" * 68)
    print("AREA 4 - VISUALIZACAO COMPUTACIONAL  (dados  ->  imagem)")
    print("=" * 68)
    vol = gerar_volume()
    print(f"Volume escalar: shape={vol.shape}  dtype={vol.dtype}  "
          f"{vol.size:,} voxels")
    print(f"  min={vol.min():.3f}  media={vol.mean():.3f}  max={vol.max():.3f}")
    print("Nenhuma cor, nenhuma opacidade, nenhuma geometria: so numeros.\n")

    fig_fatias(vol);            print("  [1/4] 01_fatias_ortogonais.png")
    fig_colormaps(vol);         print("  [2/4] 02_mapas_de_cores.png")
    fig_transferencia(vol);     print("  [3/4] 03_funcoes_de_transferencia.png")
    cont = fig_isosuperficies(vol)
    print("  [4/4] 04_isosuperficies.png")

    print("\nMalhas extraidas por marching cubes:")
    print(f"  {'isovalor':>9}{'vertices':>12}{'triangulos':>13}")
    for iso, nv, nf in cont:
        print(f"  {iso:>9.2f}{nv:>12,}{nf:>13,}")
    print("\nRepare: o isovalor e' uma ESCOLHA. Baixa-lo engloba o ruido de "
          "fundo,\nsubi-lo esconde estrutura real. Nao existe render "
          "'correto' aqui, existe\num mapeamento defensavel.")


if __name__ == "__main__":
    main()
