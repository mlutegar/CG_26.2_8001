"""
Gera os graficos das curvas de animacao (camera, Ibmec, foguete) e a tabela de animacao.
Le AP2/AP2_<AUTOR>.blend (ou <AP2_DESTINO>/...), avalia os F-Curves e plota com matplotlib.

Executar:
    blender.exe --background --python AP2/gerar_curvas.py
Saida: <DESTINO>/saida/curvas/{curvas_camera,curvas_ibmec,curvas_foguete}.png e tabela_animacao.md
(se o Python do Blender nao tiver matplotlib, usa o Python do sistema: variavel PYTHON_PLOT ou "python").
"""
import json
import os
import subprocess
import sys

import bpy

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(BASE), "AP1"))
sys.path.insert(0, BASE)
import ap1_ibmec_conceito as ap1  # noqa: E402
import ap2_ibmec_final as ap2  # noqa: E402  (projecao na camera)

DESTINO = os.path.abspath(os.environ.get("AP2_DESTINO", BASE))
BLEND = os.path.join(DESTINO, f"AP2_{ap1.AUTOR}.blend")
OUT = os.path.join(DESTINO, "saida", "curvas")
EIXO = "XYZ"

GRUPOS = {   # arquivo -> [(titulo, objeto, propriedade, indices)]
    "curvas_camera": [("Cam_Principal - location", "Cam_Principal", "location", (0, 1, 2))],
    "curvas_ibmec": [("Palavra_Ibmec - scale", "Palavra_Ibmec", "scale", (0,)),
                     ("Palavra_Ibmec - location Z", "Palavra_Ibmec", "location", (2,)),
                     ("Palavra_Ponto_i - location Z (queda)", "Palavra_Ponto_i", "location", (2,))],
    "curvas_foguete": [("Obj_Foguete - location X/Z (decolagem 270-360, 16 keys lineares)", "Obj_Foguete", "location", (0, 2)),
                       ("Obj_Foguete - velocidade em Z (u/frame): ease-in ate 306, depois constante",
                        "Obj_Foguete", "@vel", (2,)),
                       ("Obj_Foguete - rotation Y", "Obj_Foguete", "rotation_euler", (1,)),
                       ("Obj_Foguete_Chama - scale Z", "Obj_Foguete_Chama", "scale", (2,)),
                       ("Foguete na camera - posicao no quadro (0..1): terco superior direito, dentro do quadro",
                        "Obj_Foguete_Corpo", "@proj", (0, 1))],
}


def fcurves_de(idb):
    ad = idb.animation_data
    return list(ad.action.fcurves) if ad and ad.action else []


def tabela():
    linhas = ["| Objeto | Propriedade | Frames | Interpolacao |", "|---|---|---|---|"]
    fontes = [(o.name, o) for o in bpy.data.objects]
    fontes += [(f"{m.name} (material)", m.node_tree) for m in bpy.data.materials if m.node_tree]
    for nome, idb in fontes:
        grupos = {}
        for fc in fcurves_de(idb):
            chave = fc.data_path
            if fc.array_index is not None and "[" not in chave:
                pass
            grupos.setdefault(chave, []).append(fc)
        for path, fcs in grupos.items():
            frames = sorted({int(p.co[0]) for fc in fcs for p in fc.keyframe_points})
            interps = []
            for fc in fcs:
                for p in fc.keyframe_points:
                    t = p.interpolation if p.easing == "AUTO" or p.interpolation in ("LINEAR", "CONSTANT", "BEZIER") \
                        else f"{p.interpolation}/{p.easing}"
                    if p.interpolation == "BACK":
                        t = f"BACK/{p.easing}"
                    if t not in interps:
                        interps.append(t)
            prop = path.replace('nodes["', "").replace('"].inputs["', ".").replace('"].default_value', "")
            if "inputs[28]" in prop:
                prop = "Emission Strength (Principled BSDF)"
            linhas.append(f"| {nome} | {prop} | {frames[0]}-{frames[-1]} ({len(frames)} keys) | {', '.join(interps)} |")
    return "\n".join(linhas)


def amostrar():
    dados = {}
    for arq, lista in GRUPOS.items():
        paineis = []
        for titulo, nome, prop, idx in lista:
            obj = bpy.data.objects[nome]
            series = {}
            if prop == "@vel":
                fz = [fc for fc in fcurves_de(obj) if fc.data_path == "location" and fc.array_index == 2][0]
                series["dZ/dt"] = [(f, fz.evaluate(f + 1) - fz.evaluate(f)) for f in range(1, 360)]
                series["dZ/dt_keys"] = []
                paineis.append({"titulo": titulo, "series": series})
                continue
            if prop == "@proj":
                sc = bpy.context.scene
                px, py = [], []
                for f in range(1, 361):
                    sc.frame_set(f)
                    c = ap2.caixa_tela(obj, sc)
                    px.append((f, (c[0] + c[2]) / 2))
                    py.append((f, (c[1] + c[3]) / 2))
                series["x"], series["y"] = px, py
                series["x_keys"], series["y_keys"] = [], []
                paineis.append({"titulo": titulo, "series": series})
                continue
            for fc in fcurves_de(obj):
                if fc.data_path == prop and fc.array_index in idx:
                    series[EIXO[fc.array_index]] = [(f, fc.evaluate(f)) for f in range(1, 361)]
                    series[EIXO[fc.array_index] + "_keys"] = [(p.co[0], p.co[1]) for p in fc.keyframe_points]
            paineis.append({"titulo": titulo, "series": series})
        dados[arq] = paineis
    return dados


PLOT = r'''
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
dados = json.load(open(sys.argv[1])); out = sys.argv[2]
marc = [(1, "Inicio"), (73, "Desenvolvimento"), (241, "Encerramento")]
for arq, paineis in dados.items():
    fig, axs = plt.subplots(len(paineis), 1, figsize=(9, 2.6 * len(paineis) + 0.6), sharex=True)
    if len(paineis) == 1:
        axs = [axs]
    for ax, p in zip(axs, paineis):
        for nome, pts in p["series"].items():
            if nome.endswith("_keys"):
                continue
            xs, ys = zip(*pts)
            ln, = ax.plot(xs, ys, label=nome, lw=1.8)
            if p["series"][nome + "_keys"]:
                kx, ky = zip(*p["series"][nome + "_keys"])
                ax.plot(kx, ky, "o", color=ln.get_color(), ms=4)
        for f, n in marc:
            ax.axvline(f, color="gray", ls=":", lw=0.8)
        if "quadro" in p["titulo"]:
            ax.axhline(2 / 3, color="red", ls="--", lw=0.8)
            ax.set_ylim(0, 1)
        ax.set_title(p["titulo"], fontsize=9, loc="left")
        ax.grid(alpha=0.25)
        ax.legend(loc="best", fontsize=8, ncol=3)
    axs[-1].set_xlabel("frame (24 fps)  -  linhas pontilhadas: Inicio / Desenvolvimento / Encerramento")
    axs[-1].set_xlim(1, 360)
    fig.tight_layout()
    fig.savefig(f"{out}/{arq}.png", dpi=130)
    plt.close(fig)
print("plots ok")
'''


def main():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    os.makedirs(OUT, exist_ok=True)
    tab = tabela()
    with open(os.path.join(OUT, "tabela_animacao.md"), "w", encoding="utf8") as f:
        f.write(tab + "\n")
    print(tab)
    js = os.path.join(OUT, "curvas.json")
    with open(js, "w") as f:
        json.dump(amostrar(), f)
    py = os.path.join(OUT, "_plot.py")
    with open(py, "w") as f:
        f.write(PLOT)
    exe = os.environ.get("PYTHON_PLOT", "python")
    r = subprocess.run([exe, py, js, OUT], capture_output=True, text=True)
    print(r.stdout, r.stderr)
    for tmp in (js, py):
        os.remove(tmp)


if __name__ == "__main__":
    main()
