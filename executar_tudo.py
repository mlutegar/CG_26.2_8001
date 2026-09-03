"""
AC01 - Computacao Visual
Executa as quatro demonstracoes na ordem correta e grava o log completo
em log_execucao.txt (util para anexar ao relatorio como evidencia).

Uso:
    python executar_tudo.py
"""

import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))

ETAPAS = [
    ("01_sintese_imagens", "raytracer.py",
     "Sintese de imagens: cena 3D -> imagem"),
    ("02_processamento_imagens", "processamento.py",
     "Processamento de imagens: imagem -> imagem"),
    ("03_visao_computacional", "visao.py",
     "Visao computacional: imagem -> descricao"),
    ("04_visualizacao_computacional", "visualizacao.py",
     "Visualizacao computacional: dados -> imagem"),
]


def main():
    log = []
    t_total = time.time()
    for pasta, script, descricao in ETAPAS:
        cab = f"\n{'#' * 70}\n# {descricao}\n# {pasta}/{script}\n{'#' * 70}"
        print(cab)
        log.append(cab)
        t0 = time.time()
        proc = subprocess.run([sys.executable, script],
                              cwd=os.path.join(AQUI, pasta),
                              capture_output=True, text=True)
        dt = time.time() - t0
        print(proc.stdout, end="")
        log.append(proc.stdout)
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            log.append("ERRO:\n" + proc.stderr)
            with open(os.path.join(AQUI, "log_execucao.txt"), "w") as f:
                f.write("\n".join(log))
            raise SystemExit(f"Falha em {pasta}/{script}")
        rodape = f"[ok] {pasta}/{script} concluido em {dt:.1f}s"
        print(rodape)
        log.append(rodape)

    total = time.time() - t_total
    fim = f"\n{'=' * 70}\nTUDO CONCLUIDO em {total:.1f}s\n{'=' * 70}"
    print(fim)
    log.append(fim)
    with open(os.path.join(AQUI, "log_execucao.txt"), "w") as f:
        f.write("\n".join(log))
    print("Log completo salvo em log_execucao.txt")


if __name__ == "__main__":
    main()
