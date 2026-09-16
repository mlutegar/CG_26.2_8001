"""
AC02 - Computacao Grafica | Transformacoes Geometricas 2D

Resolve os 10 exercicios de transformacoes geometricas usando COORDENADAS
HOMOGENEAS: cada ponto e' representado como [x, y, 1] e cada transformacao
(translacao, escala, rotacao, reflexao, cisalhamento) e' uma matriz 3x3.

A vantagem dessa representacao e' que a translacao - que nao e' linear em 2D -
vira uma multiplicacao de matriz como as demais, e uma COMPOSICAO de
transformacoes vira simplesmente o produto das matrizes (M = M3 @ M2 @ M1).

Para cada exercicio o programa:
  1. define a geometria (ponto ou poligono),
  2. constroi a(s) matriz(es) e aplica,
  3. imprime as novas coordenadas (a resposta pedida),
  4. gera um grafico "antes/depois" em saida/.

Execucao:
    python transformacoes.py
"""

import os

import matplotlib
matplotlib.use("Agg")  # renderiza sem display, salvando PNGs
import matplotlib.pyplot as plt
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "saida")


# ---------------------------------------------------------------------------
# Matrizes de transformacao (3x3, coordenadas homogeneas)
# ---------------------------------------------------------------------------
def translacao(tx, ty):
    return np.array([[1, 0, tx],
                     [0, 1, ty],
                     [0, 0, 1]], dtype=float)


def escala(sx, sy):
    return np.array([[sx, 0, 0],
                     [0, sy, 0],
                     [0, 0, 1]], dtype=float)


def rotacao(graus):
    """Positivo = anti-horario. Para sentido horario, passe um angulo negativo."""
    t = np.radians(graus)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0],
                     [s,  c, 0],
                     [0,  0, 1]], dtype=float)


def reflexao_x():
    """Reflexao em relacao ao eixo x (y troca de sinal)."""
    return escala(1, -1)


def reflexao_y():
    """Reflexao em relacao ao eixo y (x troca de sinal)."""
    return escala(-1, 1)


def cisalhamento_h(k):
    """Cisalhamento horizontal: x' = x + k*y."""
    return np.array([[1, k, 0],
                     [0, 1, 0],
                     [0, 0, 1]], dtype=float)


def cisalhamento_v(k):
    """Cisalhamento vertical: y' = y + k*x."""
    return np.array([[1, 0, 0],
                     [k, 1, 0],
                     [0, 0, 1]], dtype=float)


def aplicar(M, pontos):
    """Aplica a matriz 3x3 M a um array Nx2 de pontos, retorna Nx2."""
    pts = np.atleast_2d(np.asarray(pontos, dtype=float))
    homog = np.hstack([pts, np.ones((pts.shape[0], 1))])  # Nx3
    out = (M @ homog.T).T                                  # Nx3
    return out[:, :2]


# ---------------------------------------------------------------------------
# Plotagem
# ---------------------------------------------------------------------------
def _fechar(poligono):
    """Repete o primeiro vertice no fim para fechar o contorno."""
    return np.vstack([poligono, poligono[0]])


def plot_formas(orig, transf, titulo, arquivo, ponto=False, rotulos=None):
    """Desenha original (solido) e transformado (tracejado) e salva em saida/."""
    fig, ax = plt.subplots(figsize=(6, 6))

    if ponto:
        o = np.atleast_2d(orig)
        t = np.atleast_2d(transf)
        ax.scatter(o[:, 0], o[:, 1], s=90, color="tab:blue", label="Original", zorder=3)
        ax.scatter(t[:, 0], t[:, 1], s=90, color="tab:red", marker="s",
                   label="Transformado", zorder=3)
        ax.annotate("P", o[0], textcoords="offset points", xytext=(8, 8))
        ax.annotate("P'", t[0], textcoords="offset points", xytext=(8, 8), color="tab:red")
    else:
        oc, tc = _fechar(np.asarray(orig)), _fechar(np.asarray(transf))
        ax.plot(oc[:, 0], oc[:, 1], "-o", color="tab:blue", label="Original")
        ax.plot(tc[:, 0], tc[:, 1], "--s", color="tab:red", label="Transformado")
        if rotulos:
            for (x, y), r in zip(np.asarray(orig), rotulos):
                ax.annotate(r, (x, y), textcoords="offset points", xytext=(6, 6))
            for (x, y), r in zip(np.asarray(transf), rotulos):
                ax.annotate(r + "'", (x, y), textcoords="offset points",
                            xytext=(6, 6), color="tab:red")

    ax.axhline(0, color="gray", lw=0.8)
    ax.axvline(0, color="gray", lw=0.8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.set_title(titulo)
    ax.legend()
    fig.tight_layout()
    caminho = os.path.join(SAIDA, arquivo)
    fig.savefig(caminho, dpi=110)
    plt.close(fig)
    return arquivo


def _fmt(pts):
    """Formata coordenadas para impressao."""
    pts = np.atleast_2d(np.asarray(pts, dtype=float))
    return ", ".join(f"({x:g}, {y:g})" for x, y in pts)


# ---------------------------------------------------------------------------
# Exercicios
# ---------------------------------------------------------------------------
def ex01():
    print("\n[Ex1] Translacao simples  P(2,3) + vetor (4,-2)")
    P = np.array([[2, 3]])
    Pl = aplicar(translacao(4, -2), P)
    print(f"    P' = {_fmt(Pl)}  (ambas as coordenadas mudam: x+4, y-2)")
    plot_formas(P, Pl, "Ex1 - Translacao P(2,3) + (4,-2)",
                "ex01_translacao.png", ponto=True)


def ex02():
    print("\n[Ex2] Escala uniforme fator 2  no triangulo A(1,1) B(3,1) C(2,4)")
    T = np.array([[1, 1], [3, 1], [2, 4]])
    Tl = aplicar(escala(2, 2), T)
    print(f"    novos vertices = {_fmt(Tl)}")
    print("    A area cresce por fator 2^2 = 4 (escala linear ao quadrado).")
    plot_formas(T, Tl, "Ex2 - Escala uniforme x2",
                "ex02_escala_uniforme.png", rotulos=["A", "B", "C"])
    return T


def ex03(T):
    print("\n[Ex3] Escala nao uniforme  sx=2, sy=0.5  no triangulo do Ex2")
    Tl = aplicar(escala(2, 0.5), T)
    print(f"    novos vertices = {_fmt(Tl)}")
    plot_formas(T, Tl, "Ex3 - Escala nao uniforme (2, 0.5)",
                "ex03_escala_nao_uniforme.png", rotulos=["A", "B", "C"])


def ex04():
    print("\n[Ex4] Rotacao de P(1,0) em 90 graus anti-horario em torno da origem")
    P = np.array([[1, 0]])
    Pl = aplicar(rotacao(90), P)
    print(f"    P' = {_fmt(Pl)}")
    plot_formas(P, Pl, "Ex4 - Rotacao 90 (anti-horario)",
                "ex04_rotacao_ponto.png", ponto=True)


def ex05():
    print("\n[Ex5] Rotacao 45 graus HORARIO do quadrado A(1,1) B(1,4) C(4,4) D(4,1)")
    Q = np.array([[1, 1], [1, 4], [4, 4], [4, 1]])
    Ql = aplicar(rotacao(-45), Q)  # horario = angulo negativo
    print(f"    novos vertices = {_fmt(Ql)}")
    plot_formas(Q, Ql, "Ex5 - Rotacao 45 (horario)",
                "ex05_rotacao_quadrado.png", rotulos=["A", "B", "C", "D"])


def ex06():
    print("\n[Ex6] Reflexao de P(2,5) em relacao ao eixo y")
    P = np.array([[2, 5]])
    Pl = aplicar(reflexao_y(), P)
    print(f"    P' = {_fmt(Pl)}")
    plot_formas(P, Pl, "Ex6 - Reflexao no eixo y",
                "ex06_reflexao_ponto.png", ponto=True)


def ex07():
    print("\n[Ex7] Reflexao no eixo x do triangulo A(2,3) B(4,3) C(3,5)")
    T = np.array([[2, 3], [4, 3], [3, 5]])
    Tl = aplicar(reflexao_x(), T)
    print(f"    novos vertices = {_fmt(Tl)}")
    plot_formas(T, Tl, "Ex7 - Reflexao no eixo x",
                "ex07_reflexao_triangulo.png", rotulos=["A", "B", "C"])


def ex08():
    print("\n[Ex8] Cisalhamento horizontal k=2 em P(2,3)   (x' = x + k*y)")
    P = np.array([[2, 3]])
    Pl = aplicar(cisalhamento_h(2), P)
    print(f"    P' = {_fmt(Pl)}")
    plot_formas(P, Pl, "Ex8 - Cisalhamento horizontal k=2",
                "ex08_cisalhamento.png", ponto=True)


def ex09():
    print("\n[Ex9] Composicao em P(3,2): translacao (1,-1) -> rot 90 anti-h -> escala 2")
    P = np.array([[3, 2]])
    M1 = translacao(1, -1)
    M2 = rotacao(90)
    M3 = escala(2, 2)
    p1 = aplicar(M1, P)
    p2 = aplicar(M2, p1)
    p3 = aplicar(M3, p2)
    print(f"    apos translacao = {_fmt(p1)}")
    print(f"    apos rotacao    = {_fmt(p2)}")
    print(f"    apos escala P'  = {_fmt(p3)}")
    # equivalente por matriz unica:
    M = M3 @ M2 @ M1
    print(f"    (matriz unica M = M3@M2@M1 confirma P' = {_fmt(aplicar(M, P))})")
    plot_formas(P, p3, "Ex9 - Composicao (transl -> rot90 -> escala2)",
                "ex09_composicao_ponto.png", ponto=True)


def ex10():
    print("\n[Ex10] Composicao no retangulo A(1,1) B(5,1) C(5,3) D(1,3):")
    print("       translacao (-2,3) -> escala (1.5, 0.5) -> reflexao no eixo y")
    R = np.array([[1, 1], [5, 1], [5, 3], [1, 3]])
    M1 = translacao(-2, 3)
    M2 = escala(1.5, 0.5)
    M3 = reflexao_y()
    M = M3 @ M2 @ M1
    Rl = aplicar(M, R)
    print(f"    novos vertices = {_fmt(Rl)}")
    plot_formas(R, Rl, "Ex10 - Composicao no retangulo",
                "ex10_composicao_retangulo.png", rotulos=["A", "B", "C", "D"])


def main():
    os.makedirs(SAIDA, exist_ok=True)
    print("=" * 70)
    print("AC02 - TRANSFORMACOES GEOMETRICAS 2D  (coordenadas homogeneas)")
    print("=" * 70)
    ex01()
    T = ex02()
    ex03(T)
    ex04()
    ex05()
    ex06()
    ex07()
    ex08()
    ex09()
    ex10()
    print("\n" + "=" * 70)
    print("10 figuras geradas em AC02_transformacoes_geometricas/saida/")
    print("=" * 70)


if __name__ == "__main__":
    main()
