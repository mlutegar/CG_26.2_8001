"""
AC02 - Transformacoes Geometricas
Roda transformacoes.py e grava a saida de console em log_ac2.txt
(util para anexar ao relatorio como evidencia).

Uso:
    python executar_ac2.py
"""

import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    t0 = time.time()
    proc = subprocess.run([sys.executable, "transformacoes.py"],
                          cwd=AQUI, capture_output=True, text=True)
    dt = time.time() - t0
    print(proc.stdout, end="")
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
    rodape = f"\n[ok] transformacoes.py concluido em {dt:.1f}s"
    print(rodape)
    with open(os.path.join(AQUI, "log_ac2.txt"), "w") as f:
        f.write(proc.stdout + (proc.stderr or "") + rodape + "\n")
    print("Log salvo em log_ac2.txt")
    if proc.returncode != 0:
        raise SystemExit("Falha na execucao de transformacoes.py")


if __name__ == "__main__":
    main()
