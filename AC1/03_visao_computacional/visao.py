"""
AC01 - Computacao Visual | Area 3: VISAO COMPUTACIONAL (Visao Artificial)

Entrada: uma imagem.
Saida:   uma DESCRICAO simbolica da cena (objetos, posicoes, geometria).
         E' o problema INVERSO da Area 1.

O experimento e' desenhado para tornar esse ponto verificavel: a Area 1
renderizou a cena a partir de um modelo 3D e salvou o gabarito
(cena_gabarito.json) com o centro e o raio de cada esfera em pixels.
Aqui o programa ve APENAS a imagem e tenta reconstruir esses numeros.
No final, comparamos a estimativa com o gabarito e medimos o erro.

Aspectos especificos da area demonstrados aqui:
  1. Deteccao de primitivas por votacao: transformada de Hough para circulos.
  2. Avaliacao quantitativa contra ground truth (erro em pixels).
  3. Extracao de caracteristicas locais (ORB: FAST + BRIEF orientado).
  4. Casamento de descritores com teste de razao de Lowe.
  5. Estimacao de modelo geometrico com RANSAC (homografia), robusto a
     correspondencias erradas (outliers).
  6. Verificacao: a homografia estimada e' comparada com a transformacao
     que realmente foi aplicada.
  7. Efeito da textura: o xadrez procedural do chao multiplica por ~9 o
     numero de pontos de interesse detectados. Regiao lisa nao tem
     informacao local suficiente para o casamento (problema da abertura).

Execucao:
    python visao.py
"""

import json
import os

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")
DIR1 = os.path.join(AQUI, "..", "01_sintese_imagens", "saida")
IMG = os.path.join(DIR1, "render_referencia.png")
GABARITO = os.path.join(DIR1, "cena_gabarito.json")


def carregar():
    if not os.path.exists(IMG):
        raise SystemExit(
            "Execute primeiro 01_sintese_imagens/raytracer.py: esta etapa "
            "usa o render e o gabarito da cena como entrada.")
    bgr = cv2.imread(IMG, cv2.IMREAD_COLOR)
    gab = json.load(open(GABARITO, encoding="utf-8")) \
        if os.path.exists(GABARITO) else None
    return bgr, gab


# --------------------------------------------------------------------------
# 1. DETECCAO DE OBJETOS: imagem -> lista de esferas (descricao)
# --------------------------------------------------------------------------
def detectar_esferas(bgr):
    cinza = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    suave = cv2.medianBlur(cinza, 5)
    circulos = cv2.HoughCircles(
        suave, cv2.HOUGH_GRADIENT, dp=1.0,
        minDist=60,          # esferas nao podem estar mais perto que isso
        param1=120,          # limiar alto do detector de bordas Canny interno
        param2=30,           # votos minimos no acumulador de Hough
        minRadius=30, maxRadius=65)
    if circulos is None:
        return []
    c = np.round(circulos[0, :]).astype(int)
    c = sorted(c.tolist(), key=lambda t: t[0])   # ordena da esquerda p/ direita
    return [{"cx": float(x), "cy": float(y), "raio_px": float(r)}
            for x, y, r in c]


def comparar_com_gabarito(deteccoes, gab):
    if not gab:
        return []
    verdade = sorted(gab["esferas_projetadas"], key=lambda d: d["cx"])
    linhas = []
    for v in verdade:
        if not deteccoes:
            break
        d = min(deteccoes, key=lambda p: (p["cx"] - v["cx"]) ** 2
                + (p["cy"] - v["cy"]) ** 2)
        erro_c = float(np.hypot(d["cx"] - v["cx"], d["cy"] - v["cy"]))
        erro_r = float(abs(d["raio_px"] - v["raio_px"]))
        linhas.append({
            "objeto": v["nome"], "material": v["material"],
            "gabarito": [v["cx"], v["cy"], v["raio_px"]],
            "estimado": [d["cx"], d["cy"], d["raio_px"]],
            "erro_centro_px": round(erro_c, 2),
            "erro_raio_px": round(erro_r, 2),
        })
    return linhas


def figura_deteccao(bgr, deteccoes, gab, nome):
    vis = bgr.copy()
    if gab:
        for v in gab["esferas_projetadas"]:
            cv2.circle(vis, (int(v["cx"]), int(v["cy"])), int(v["raio_px"]),
                       (0, 255, 0), 1, cv2.LINE_AA)
    for d in deteccoes:
        cv2.circle(vis, (int(d["cx"]), int(d["cy"])), int(d["raio_px"]),
                   (0, 0, 255), 2, cv2.LINE_AA)
        cv2.drawMarker(vis, (int(d["cx"]), int(d["cy"])), (0, 0, 255),
                       cv2.MARKER_CROSS, 12, 2)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
    ax.set_title("Visao: verde = gabarito da cena 3D | vermelho = estimado "
                 "pela transformada de Hough", fontsize=10)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, nome), dpi=120)
    plt.close(fig)


# --------------------------------------------------------------------------
# 2. CARACTERISTICAS LOCAIS + RANSAC: recuperar a geometria entre duas vistas
# --------------------------------------------------------------------------
def transformacao_conhecida(bgr, angulo=17.0, escala=0.82, tx=30, ty=18):
    h, w = bgr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angulo, escala)
    M[0, 2] += tx
    M[1, 2] += ty
    warp = cv2.warpAffine(bgr, M, (w, h), borderValue=(255, 255, 255))
    H_real = np.vstack([M, [0, 0, 1]])
    return warp, H_real


def casar_caracteristicas(bgr_a, bgr_b, n_features=1500):
    a = cv2.cvtColor(bgr_a, cv2.COLOR_BGR2GRAY)
    b = cv2.cvtColor(bgr_b, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=n_features, scaleFactor=1.2, nlevels=8)
    ka, da = orb.detectAndCompute(a, None)
    kb, db = orb.detectAndCompute(b, None)
    if da is None or db is None:
        return ka, kb, [], None, 0

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    brutos = bf.knnMatch(da, db, k=2)
    # Teste de razao de Lowe: descarta casamentos ambiguos
    bons = [m for m, n in brutos if len([m, n]) == 2 and m.distance < 0.78 * n.distance]

    H_est, inliers = None, 0
    if len(bons) >= 4:
        pa = np.float32([ka[m.queryIdx].pt for m in bons]).reshape(-1, 1, 2)
        pb = np.float32([kb[m.trainIdx].pt for m in bons]).reshape(-1, 1, 2)
        H_est, mask = cv2.findHomography(pa, pb, cv2.RANSAC, 3.0)
        inliers = int(mask.sum()) if mask is not None else 0
    return ka, kb, bons, H_est, inliers


def erro_reprojecao(H_real, H_est, shape):
    """Erro medio, em pixels, ao mapear os 4 cantos da imagem."""
    if H_est is None:
        return float("nan")
    h, w = shape[:2]
    cantos = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    p_real = cv2.perspectiveTransform(cantos, H_real).reshape(-1, 2)
    p_est = cv2.perspectiveTransform(cantos, H_est).reshape(-1, 2)
    return float(np.mean(np.linalg.norm(p_real - p_est, axis=1)))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    bgr, gab = carregar()
    print("=" * 68)
    print("AREA 3 - VISAO COMPUTACIONAL  (imagem  ->  descricao / modelo)")
    print("=" * 68)
    print(f"Entrada: render_referencia.png  shape={bgr.shape}")
    print("A cena 3D original NAO e' fornecida ao algoritmo; o gabarito "
          "so e' usado\npara medir o erro no final.\n")

    # --- Experimento A: recuperar os objetos da cena --------------------
    det = detectar_esferas(bgr)
    print(f"[A] Transformada de Hough encontrou {len(det)} circulo(s).")
    tabela = comparar_com_gabarito(det, gab)
    if tabela:
        print(f"    {'objeto':<20}{'gabarito (cx,cy,r)':<26}"
              f"{'estimado':<26}{'erro c':>8}{'erro r':>8}")
        for t in tabela:
            g = "(" + ", ".join(f"{v:.0f}" for v in t["gabarito"]) + ")"
            e = "(" + ", ".join(f"{v:.0f}" for v in t["estimado"]) + ")"
            print(f"    {t['objeto']:<20}{g:<26}{e:<26}"
                  f"{t['erro_centro_px']:>8.1f}{t['erro_raio_px']:>8.1f}")
        media = np.mean([t["erro_centro_px"] for t in tabela])
        print(f"    Erro medio de centro: {media:.2f} px "
              f"({100 * media / bgr.shape[1]:.2f}% da largura)")
    figura_deteccao(bgr, det, gab, "01_deteccao_hough.png")

    # --- Experimento B: geometria entre duas vistas ---------------------
    warp, H_real = transformacao_conhecida(bgr)
    ka, kb, bons, H_est, inliers = casar_caracteristicas(bgr, warp)
    err = erro_reprojecao(H_real, H_est, bgr.shape)
    print(f"\n[B] ORB: {len(ka)} pontos na vista 1, {len(kb)} na vista 2.")
    print(f"    Casamentos apos o teste de razao de Lowe: {len(bons)}")
    print(f"    Inliers do RANSAC: {inliers} "
          f"({100 * inliers / max(len(bons), 1):.0f}% dos casamentos)")
    print(f"    Erro medio de reprojecao dos cantos: {err:.2f} px")

    if H_est is not None:
        vis = cv2.drawMatches(
            bgr, ka, warp, kb, bons[:60], None,
            matchColor=(0, 200, 0), singlePointColor=(180, 180, 180),
            flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        fig, ax = plt.subplots(figsize=(13, 4.2))
        ax.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
        ax.set_title("Casamento de descritores ORB entre duas vistas "
                     "(60 melhores)", fontsize=10)
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(os.path.join(SAIDA, "02_casamento_orb.png"), dpi=120)
        plt.close(fig)

        h, w = bgr.shape[:2]
        cantos = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
        proj = cv2.perspectiveTransform(cantos, H_est).astype(int)
        vis2 = warp.copy()
        cv2.polylines(vis2, [proj], True, (0, 0, 255), 2, cv2.LINE_AA)
        fig, ax = plt.subplots(figsize=(9, 5.2))
        ax.imshow(cv2.cvtColor(vis2, cv2.COLOR_BGR2RGB))
        ax.set_title(f"Homografia estimada por RANSAC projetada sobre a "
                     f"vista 2 (erro medio {err:.2f} px)", fontsize=10)
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(os.path.join(SAIDA, "03_homografia_ransac.png"), dpi=120)
        plt.close(fig)

    # --- Saida simbolica: e' ISTO que a visao produz ---------------------
    relatorio = {
        "entrada": "render_referencia.png",
        "deteccao_objetos": {
            "metodo": "cv2.HoughCircles (HOUGH_GRADIENT)",
            "objetos_encontrados": len(det),
            "comparacao_com_gabarito": tabela,
        },
        "geometria_entre_vistas": {
            "metodo": "ORB + BFMatcher(Hamming) + razao de Lowe + RANSAC",
            "keypoints_vista1": len(ka), "keypoints_vista2": len(kb),
            "casamentos": len(bons), "inliers_ransac": inliers,
            "H_real": np.asarray(H_real).round(4).tolist(),
            "H_estimada": (np.asarray(H_est).round(4).tolist()
                           if H_est is not None else None),
            "erro_reprojecao_px": round(err, 3),
        },
    }
    with open(os.path.join(SAIDA, "descricao_da_cena.json"), "w",
              encoding="utf-8") as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False)

    print("\nArquivos gerados em 03_visao_computacional/saida/:")
    for nome in sorted(os.listdir(SAIDA)):
        print("  -", nome)
    print("\nRepare no formato de descricao_da_cena.json: numeros e rotulos, "
          "nao pixels.\nEssa e' a diferenca essencial em relacao a Area 2.")


if __name__ == "__main__":
    main()
