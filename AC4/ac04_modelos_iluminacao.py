"""
AC04 - Computacao Grafica | Lambert x Phong x Blinn-Phong na cena Ibmec (AP1)
Blender 4.5 LTS (bpy)

Abre a cena da AP1, salva copia como AC04_MichelLutegar.blend (original intacto),
cria luzes fixas, os materiais MAT_Lambert / MAT_Phong / MAT_BlinnPhong, aplica um
em cada objeto autoral, e renderiza: final, comparacao (3 closes) e teste de angulo.

Executar:
    blender.exe --background --python AC4/ac04_modelos_iluminacao.py
"""
import math
import os
import shutil

import bpy
from mathutils import Vector

AUTOR = "MichelLutegar"
BASE = os.path.dirname(os.path.abspath(__file__))
AP1_BLEND = os.path.normpath(os.path.join(BASE, "..", "AP1", "saida",
                                          f"AP1_{AUTOR}.blend"))
DESTINO = os.path.join(BASE, f"AC04_{AUTOR}.blend")
VAULT_IMG = os.path.normpath(os.path.join(
    BASE, "..", "obsidian-CG_26.2_8001", "5-AC04", "img"))

# ---- iluminacao FIXA (mesmos valores no relatorio) ----
SOL = dict(energia=4.0, cor=(1.0, 1.0, 1.0),
           rot_graus=(50.0, 0.0, 35.0), angulo_graus=1.5)
FILL = dict(energia=250.0, cor=(0.85, 0.9, 1.0), tamanho=8.0,
            loc=(-5.0, -6.0, 5.0))

# ---- materiais: (nome, objeto-malha, cor, rugosidade, specular IOR level) ----
MATERIAIS = [
    ("MAT_Lambert", "Obj_Computador_Corpo", (0.20, 0.35, 0.80, 1.0), 1.0, 0.0),
    ("MAT_Phong", "Obj_Robo_Corpo", (0.05, 0.65, 0.45, 1.0), 0.20, 0.5),
    ("MAT_BlinnPhong", "Obj_Foguete_Corpo", (0.80, 0.08, 0.08, 1.0), 0.10, 0.8),
]
# (nome do grupo do objeto, deslocamento da camera p/ close)
CLOSES = [("Obj_Computador", Vector((2.5, -8.0, 1.2))),
          ("Obj_Robo", Vector((1.0, -11.0, 1.5))),
          ("Obj_Foguete", Vector((-1.5, -9.0, 0.8)))]


def mover_para(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def criar_luzes(raiz):
    for o in list(bpy.data.objects):
        if o.type == "LIGHT":
            bpy.data.objects.remove(o, do_unlink=True)
    col = bpy.data.collections.new("Luzes")
    raiz.children.link(col)

    d = bpy.data.lights.new("LUZ_Principal", "SUN")
    d.energy = SOL["energia"]
    d.color = SOL["cor"]
    d.angle = math.radians(SOL["angulo_graus"])
    sol = bpy.data.objects.new("LUZ_Principal", d)
    col.objects.link(sol)
    sol.rotation_euler = [math.radians(a) for a in SOL["rot_graus"]]

    f = bpy.data.lights.new("LUZ_Preenchimento", "AREA")
    f.energy = FILL["energia"]
    f.color = FILL["cor"]
    f.size = FILL["tamanho"]
    fill = bpy.data.objects.new("LUZ_Preenchimento", f)
    col.objects.link(fill)
    fill.location = FILL["loc"]
    alvo = bpy.data.objects["Alvo_Camera"]
    c = fill.constraints.new("TRACK_TO")
    c.target = alvo
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    return sol


def criar_materiais(raiz):
    col = bpy.data.collections.new("Materiais_AC04")
    raiz.children.link(col)
    for nome, alvo, cor, rough, spec in MATERIAIS:
        mat = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
        mat.use_nodes = True
        mat.diffuse_color = cor
        b = mat.node_tree.nodes.get("Principled BSDF")
        b.inputs["Base Color"].default_value = cor
        b.inputs["Metallic"].default_value = 0.0
        b.inputs["Roughness"].default_value = rough
        b.inputs["Specular IOR Level"].default_value = spec
        for k in ("Coat Weight", "Sheen Weight"):
            if k in b.inputs:
                b.inputs[k].default_value = 0.0
        o = bpy.data.objects[alvo]
        o.data.materials.clear()
        o.data.materials.append(mat)
        print(f"[AC04] {nome} -> {alvo}  rough={rough} spec={spec}")


def render(caminho, w, h, amostras=64):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.samples = amostras
    s.cycles.use_denoising = True
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


def montar_lado_a_lado(arquivos, saida):
    import numpy as np
    imgs = []
    for a in arquivos:
        im = bpy.data.images.load(a)
        w, h = im.size
        imgs.append(np.array(im.pixels[:]).reshape(h, w, 4))
    out = np.concatenate(imgs, axis=1)
    res = bpy.data.images.new("comparacao", out.shape[1], out.shape[0])
    res.pixels = out.ravel().tolist()
    res.filepath_raw = saida
    res.file_format = "PNG"
    res.save()


def main():
    bpy.ops.wm.open_mainfile(filepath=AP1_BLEND)
    bpy.ops.wm.save_as_mainfile(filepath=DESTINO)   # copia: original intacto
    raiz = bpy.data.collections["AP1_Ibmec_Conceito"]
    sol = criar_luzes(raiz)
    criar_materiais(raiz)

    cam = bpy.data.objects["Cam_Principal"]
    alvo = bpy.data.objects["Alvo_Camera"]
    bpy.context.scene.camera = cam
    cam0, alvo0 = cam.location.copy(), alvo.location.copy()
    rot0 = sol.rotation_euler.copy()
    lens0 = cam.data.lens

    # 1) render final
    render(os.path.join(BASE, "AC04_render_final.png"), 1920, 1080, 96)

    # 2) comparacao: 3 closes, mesma luz
    arqs = []
    # a palavra fica oculta SO nos closes (nao e alterada), para nao tapar o robo
    ocultos = [bpy.data.objects["Palavra_Ibmec"], bpy.data.objects["Palavra_Ponto_i"]]
    for o in ocultos:
        o.hide_render = True
    for nome, off in CLOSES:
        corpo = bpy.data.objects[nome + "_Corpo"]
        cantos = [corpo.matrix_world @ Vector(c) for c in corpo.bound_box]
        centro = sum(cantos, Vector()) / 8.0
        cam.data.lens = 85
        alvo.location = centro
        cam.location = centro + off
        bpy.context.view_layer.update()
        p = os.path.join(BASE, f"_close_{nome}.png")
        render(p, 800, 800, 64)
        arqs.append(p)
    for o in ocultos:
        o.hide_render = False
    cam.data.lens = lens0
    alvo.location, cam.location = alvo0, cam0
    montar_lado_a_lado(arqs, os.path.join(BASE, "AC04_comparacao.png"))
    for a in arqs:
        os.remove(a)

    # 3) teste de angulo: gira a luz temporariamente, renderiza, restaura
    sol.rotation_euler = (math.radians(25), 0.0, math.radians(-60))
    render(os.path.join(BASE, "AC04_teste_angulo.png"), 1280, 720, 64)
    sol.rotation_euler = rot0
    bpy.context.view_layer.update()

    for f in list(bpy.data.fonts):
        if f.users == 0:
            bpy.data.fonts.remove(f)
    bpy.ops.wm.save_as_mainfile(filepath=DESTINO)
    print("[AC04] salvo:", DESTINO)

    os.makedirs(VAULT_IMG, exist_ok=True)
    for n in ("AC04_render_final.png", "AC04_comparacao.png",
              "AC04_teste_angulo.png"):
        shutil.copy2(os.path.join(BASE, n), os.path.join(VAULT_IMG, n))


if __name__ == "__main__":
    main()
