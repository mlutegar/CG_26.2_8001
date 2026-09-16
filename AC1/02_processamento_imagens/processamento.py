"""
AC01 - Computacao Visual | Area 2: PROCESSAMENTO DIGITAL DE IMAGENS

Entrada: uma imagem.
Saida:   outra imagem (ou uma medida sobre ela). NAO ha interpretacao
         semantica: o programa nunca "sabe" que existem esferas na cena.

Usa como entrada a imagem produzida pela Area 1 (o render do ray tracer),
o que deixa explicito o encadeamento entre as areas. Se o render nao
existir, cai para uma imagem de exemplo do scikit-image.

Aspectos especificos da area demonstrados aqui:
  1. Operacoes pontuais e histograma: equalizacao global e CLAHE.
  2. Dominio espacial: convolucao com nucleos (media, gaussiano, Sobel).
  3. Filtro nao linear: mediana (unico que remove sal-e-pimenta).
  4. Dominio da frequencia: FFT 2D, espectro de magnitude, passa-baixa
     ideal (com o artefato de "ringing") x passa-baixa gaussiano.
  5. Equivalencia teorema da convolucao: filtrar no espaco == multiplicar
     no dominio da frequencia.
  6. Morfologia matematica sobre imagem binaria: erosao, dilatacao,
     abertura e fechamento.
  7. Avaliacao objetiva com PSNR e SSIM (metricas de fidelidade).

Execucao:
    python processamento.py
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from skimage import color, data, exposure, img_as_float, io, morphology, util
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
ENTRADA = os.path.join(AQUI, "..", "01_sintese_imagens", "saida",
                       "render_referencia.png")


def carregar():
    if os.path.exists(ENTRADA):
        img = img_as_float(io.imread(ENTRADA))[..., :3]
        origem = "render do ray tracer (Area 1)"
    else:
        img = img_as_float(data.astronaut())
        origem = "scikit-image data.astronaut() (fallback)"
    return img, color.rgb2gray(img), origem


def salvar(fig, nome):
    caminho = os.path.join(SAIDA, nome)
    fig.tight_layout()
    fig.savefig(caminho, dpi=110)
    plt.close(fig)
    return nome


# --------------------------------------------------------------------------
# 1. HISTOGRAMA E OPERACOES PONTUAIS
# --------------------------------------------------------------------------
def etapa_histograma(cinza):
    equalizada = exposure.equalize_hist(cinza)
    clahe = exposure.equalize_adapthist(cinza, clip_limit=0.02)

    fig, ax = plt.subplots(2, 3, figsize=(12, 6))
    for j, (im, tit) in enumerate([(cinza, "original"),
                                   (equalizada, "equalizacao global"),
                                   (clahe, "CLAHE (adaptativa)")]):
        ax[0, j].imshow(im, cmap="gray", vmin=0, vmax=1)
        ax[0, j].set_title(tit, fontsize=10)
        ax[0, j].axis("off")
        ax[1, j].hist(im.ravel(), bins=256, range=(0, 1), color="#534AB7")
        ax[1, j].set_xlabel("intensidade")
        ax[1, j].set_yticks([])
    fig.suptitle("Operacoes pontuais: o histograma e' redistribuido, "
                 "a geometria da cena nao muda", fontsize=12)
    return salvar(fig, "01_histograma_equalizacao.png"), clahe


# --------------------------------------------------------------------------
# 2. RUIDO E FILTRAGEM NO DOMINIO ESPACIAL
# --------------------------------------------------------------------------
def etapa_ruido(cinza):
    rng = np.random.default_rng(7)
    gauss = np.clip(cinza + rng.normal(0, 0.08, cinza.shape), 0, 1)
    sal = util.random_noise(cinza, mode="s&p", amount=0.06, rng=7)

    restauracoes = {
        "media 5x5": lambda x: ndimage.uniform_filter(x, size=5),
        "gaussiano s=1.5": lambda x: ndimage.gaussian_filter(x, sigma=1.5),
        "mediana 5x5": lambda x: ndimage.median_filter(x, size=5),
    }

    linhas = []
    fig, ax = plt.subplots(2, 4, figsize=(14, 6.4))
    for i, (nome_ruido, ruidosa) in enumerate([("gaussiano", gauss),
                                               ("sal e pimenta", sal)]):
        ax[i, 0].imshow(ruidosa, cmap="gray", vmin=0, vmax=1)
        ax[i, 0].set_title(f"ruido {nome_ruido}\nPSNR="
                           f"{psnr(cinza, ruidosa, data_range=1.0):.1f} dB",
                           fontsize=9)
        ax[i, 0].axis("off")
        linhas.append([nome_ruido, "sem filtro",
                       round(psnr(cinza, ruidosa, data_range=1.0), 2),
                       round(ssim(cinza, ruidosa, data_range=1.0), 4)])
        for j, (nome_f, f) in enumerate(restauracoes.items(), start=1):
            rec = f(ruidosa)
            p = psnr(cinza, rec, data_range=1.0)
            s = ssim(cinza, rec, data_range=1.0)
            linhas.append([nome_ruido, nome_f, round(p, 2), round(s, 4)])
            ax[i, j].imshow(rec, cmap="gray", vmin=0, vmax=1)
            ax[i, j].set_title(f"{nome_f}\nPSNR={p:.1f} dB  SSIM={s:.3f}",
                               fontsize=9)
            ax[i, j].axis("off")
    fig.suptitle("Restauracao: a mediana e' o unico filtro que trata bem "
                 "sal-e-pimenta (nao linear)", fontsize=12)
    nome = salvar(fig, "02_ruido_e_filtros.png")

    with open(os.path.join(SAIDA, "metricas.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ruido", "filtro", "PSNR_dB", "SSIM"])
        w.writerows(linhas)
    return nome, linhas


# --------------------------------------------------------------------------
# 3. CONVOLUCAO: DETECCAO DE BORDAS
# --------------------------------------------------------------------------
def etapa_convolucao(cinza):
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    ky = kx.T
    gx = ndimage.convolve(cinza, kx)
    gy = ndimage.convolve(cinza, ky)
    mag = np.hypot(gx, gy)
    mag /= mag.max()

    fig, ax = plt.subplots(1, 4, figsize=(14, 3.6))
    for a, im, tit in zip(ax, [cinza, gx, gy, mag],
                          ["original", "Sobel horizontal (dI/dx)",
                           "Sobel vertical (dI/dy)", "magnitude do gradiente"]):
        a.imshow(im, cmap="gray")
        a.set_title(tit, fontsize=10)
        a.axis("off")
    fig.suptitle("Dominio espacial: convolucao 3x3 estima a derivada da "
                 "imagem", fontsize=12)
    return salvar(fig, "03_convolucao_sobel.png"), mag


# --------------------------------------------------------------------------
# 4. DOMINIO DA FREQUENCIA
# --------------------------------------------------------------------------
def _mascara_radial(shape, raio):
    h, w = shape
    y, x = np.ogrid[:h, :w]
    d = np.hypot(y - h / 2, x - w / 2)
    return d <= raio


def etapa_frequencia(cinza):
    # A analise usa um recorte QUADRADO: em imagem retangular, uma mascara
    # radial no grid de indices corresponde a frequencias diferentes em x e y.
    n = min(cinza.shape)
    y0 = (cinza.shape[0] - n) // 2
    x0 = (cinza.shape[1] - n) // 2
    img = cinza[y0:y0 + n, x0:x0 + n]

    F = np.fft.fftshift(np.fft.fft2(img))
    espectro = np.log1p(np.abs(F))

    raio = 24
    ideal = _mascara_radial(img.shape, raio).astype(float)
    yy, xx = np.ogrid[:n, :n]
    d2 = (yy - n / 2) ** 2 + (xx - n / 2) ** 2
    gaussiana = np.exp(-d2 / (2.0 * raio ** 2))

    rec_ideal = np.real(np.fft.ifft2(np.fft.ifftshift(F * ideal)))
    rec_gauss = np.real(np.fft.ifft2(np.fft.ifftshift(F * gaussiana)))
    # Mesma suavizacao feita no dominio espacial (teorema da convolucao).
    # mode="wrap" reproduz a convolucao circular implicita na FFT.
    sigma_espacial = n / (2 * np.pi * raio)
    rec_espacial = ndimage.gaussian_filter(img, sigma=sigma_espacial,
                                           mode="wrap")
    dif = np.abs(rec_gauss - rec_espacial)

    fig, ax = plt.subplots(2, 3, figsize=(12.5, 7.4))
    painel = [
        (img, f"original (recorte {n}x{n})"),
        (espectro, "espectro de magnitude log|F(u,v)|"),
        (ideal, f"mascara passa-baixa ideal (r={raio})"),
        (rec_ideal, "passa-baixa ideal -> ringing"),
        (rec_gauss, "passa-baixa gaussiano (frequencia)"),
        (dif, f"|freq - espaco| (max={dif.max():.5f})"),
    ]
    for a, (im, tit) in zip(ax.ravel(), painel):
        a.imshow(im, cmap="gray")
        a.set_title(tit, fontsize=9)
        a.axis("off")
    fig.suptitle("Dominio da frequencia: filtrar = multiplicar o espectro; "
                 "o corte abrupto gera artefatos", fontsize=12)
    return salvar(fig, "04_dominio_frequencia.png"), float(dif.max())


# --------------------------------------------------------------------------
# 5. MORFOLOGIA MATEMATICA
# --------------------------------------------------------------------------
def etapa_morfologia(cinza):
    limiar = cinza.mean()
    binaria = cinza > limiar
    rng = np.random.default_rng(3)
    sujeira = rng.random(binaria.shape) < 0.03
    binaria_ruidosa = np.logical_xor(binaria, sujeira)

    elem = morphology.disk(2)
    ops = {
        "erosao": ndimage.binary_erosion(binaria_ruidosa, elem),
        "dilatacao": ndimage.binary_dilation(binaria_ruidosa, elem),
        "abertura": ndimage.binary_opening(binaria_ruidosa, elem),
        "fechamento": ndimage.binary_closing(binaria_ruidosa, elem),
    }

    fig, ax = plt.subplots(1, 5, figsize=(15, 3.2))
    ax[0].imshow(binaria_ruidosa, cmap="gray")
    ax[0].set_title(f"binarizada (limiar={limiar:.2f})\n+ 3% de ruido",
                    fontsize=9)
    ax[0].axis("off")
    for a, (nome, im) in zip(ax[1:], ops.items()):
        a.imshow(im, cmap="gray")
        a.set_title(f"{nome} (disco r=2)", fontsize=9)
        a.axis("off")
    fig.suptitle("Morfologia matematica: operadores de conjunto sobre a "
                 "forma dos objetos", fontsize=12)
    return salvar(fig, "05_morfologia.png")


def main():
    os.makedirs(SAIDA, exist_ok=True)
    img, cinza, origem = carregar()
    print("=" * 68)
    print("AREA 2 - PROCESSAMENTO DE IMAGENS  (imagem  ->  imagem)")
    print("=" * 68)
    print(f"Entrada: {origem}  |  shape={img.shape}")

    n1, _ = etapa_histograma(cinza)
    print(f"  [1/5] {n1}")
    n2, linhas = etapa_ruido(cinza)
    print(f"  [2/5] {n2}  (+ metricas.csv)")
    n3, _ = etapa_convolucao(cinza)
    print(f"  [3/5] {n3}")
    n4, dif = etapa_frequencia(cinza)
    print(f"  [4/5] {n4}")
    n5 = etapa_morfologia(cinza)
    print(f"  [5/5] {n5}")

    print("\nMetricas de restauracao (PSNR maior = melhor):")
    print(f"  {'ruido':<16}{'filtro':<18}{'PSNR (dB)':>10}{'SSIM':>9}")
    for r, f, p, s in linhas:
        print(f"  {r:<16}{f:<18}{p:>10.2f}{s:>9.4f}")
    print(f"\nDiferenca maxima entre filtrar no espaco e na frequencia: "
          f"{dif:.5f}")
    print("Isso confirma na pratica o teorema da convolucao.")


if __name__ == "__main__":
    main()
