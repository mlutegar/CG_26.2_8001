"""
AC05 - Computacao Grafica | Materiais PBR e texturas na cena Ibmec (AP1/AC04)
Blender 4.5 LTS (bpy)

Reconstroi a cena da AC04 (mesmas luzes, camera e enquadramento, reaproveitando
as funcoes de AC4/ac04_modelos_iluminacao.py por import) e troca os materiais
Lambert/Phong/Blinn-Phong por materiais PBR (Principled BSDF):

    Palavra_Ibmec         -> MAT_Ibmec_PBR (azul da marca, sem textura)
    Palavra_Ponto_i       -> MAT_Ibmec_Ponto_PBR (laranja da marca, sem textura)
    Obj_Computador_Corpo  -> MAT_Madeira_PBR (Base Color + Roughness + Normal)
    Obj_Foguete_Corpo     -> MAT_Metal_Escovado_PBR (Base Color + Roughness + Normal)
    Obj_Robo_Corpo        -> MAT_Espelho_PBR (Metallic 1, Roughness baixo)
    World                 -> cinza da AC04 para camera/luz difusa + HDRI de estudio
                             (Poly Haven, CC0) so para raios glossy (reflexos)

Texturas em AC5/texturas (fontes em FONTES.md). Empacota as imagens no .blend e
renderiza em Cycles (principal) e Eevee (comparacao).

Executar (a partir da raiz do repositorio):
    blender.exe --background --python AC5/ac05_materiais_texturas.py
Para gerar em outra pasta (testes), sem alterar AC5/:
    set AC05_DESTINO=C:\temp\teste_ac05
"""
import math
import os
import sys
import time

import bpy

BASE = os.path.dirname(os.path.abspath(__file__))
RAIZ_REPO = os.path.normpath(os.path.join(BASE, ".."))
# as pastas das atividades anteriores nao sao pacotes: entram no sys.path
for _p in (os.path.join(RAIZ_REPO, "AP1"), os.path.join(RAIZ_REPO, "AC4")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ap1_ibmec_conceito as ap1          # noqa: E402  (AUTOR e cores da marca)
import ac04_modelos_iluminacao as ac04    # noqa: E402  (luzes, render, AP1_BLEND)

AUTOR = ap1.AUTOR
# Pasta de saida configuravel: AC05_DESTINO=<pasta> (padrao: AC5/). O .blend vai
# para a pasta e os renders para <pasta>/saida. Texturas sempre de AC5/texturas.
PASTA_DESTINO = os.environ.get("AC05_DESTINO") or BASE
DESTINO = os.path.join(PASTA_DESTINO, f"AC05_{AUTOR}.blend")
TEX = os.path.join(BASE, "texturas")
SAIDA = os.path.join(PASTA_DESTINO, "saida")
UV_NOME = "UV_AC05"

# ---- arquivos de textura (CC0) ----
MADEIRA = dict(
    cor=os.path.join(TEX, "wood", "brown_planks_03_diff_1k.jpg"),
    rough=os.path.join(TEX, "wood", "brown_planks_03_rough_1k.jpg"),
    normal=os.path.join(TEX, "wood", "brown_planks_03_nor_gl_1k.jpg"),
)
METAL = dict(
    cor=os.path.join(TEX, "Metal009", "Metal009_1K-JPG_Color.jpg"),
    rough=os.path.join(TEX, "Metal009", "Metal009_1K-JPG_Roughness.jpg"),
    normal=os.path.join(TEX, "Metal009", "Metal009_1K-JPG_NormalGL.jpg"),
)
# lado (em unidades da cena) que cada tile de textura representa
TILE_MADEIRA_M = 2.5   # tile de 1 m no Poly Haven; 2.5 deixa as tabuas legiveis na camera
TILE_METAL_M = 0.8     # ajustado visualmente para as estrias nao ficarem grossas

# Valores dos materiais (mesmos do relatorio)
IBMEC_ROUGH = 0.45
MADEIRA_NORMAL_FORCA = 1.0
METAL_ROUGH_MIN, METAL_ROUGH_MAX = 0.30, 0.50
METAL_NORMAL_FORCA = 0.8
ESPELHO_COR = (0.95, 0.95, 0.95, 1.0)
ESPELHO_ROUGH = 0.02
HDRI = os.path.join(TEX, "hdri", "studio_small_08_1k.hdr")
HDRI_FORCA = 1.0
REFLETOR_FORCA = 8.0
USAR_REFLETORES = os.environ.get("AC05_REFLETORES") == "1"  # com o HDRI nao sao necessarios
COLECAO_AUX = "AC05_Materiais_Texturas"


# --------------------------------------------------------------------------
# UV
# --------------------------------------------------------------------------
def marcar_seams_atras(obj, camera):
    """Marca seams via bmesh para o foguete: (1) arestas vivas (diedro > 60
    graus, separam aletas e bocal do tubo) e (2) uma linha longitudinal no lado
    de tras do corpo, oposto a camera. O tubo abre por essa linha e a emenda das
    estrias fica escondida atras do foguete."""
    import bmesh
    from mathutils import Vector
    me = obj.data
    # direcao horizontal camera -> objeto, levada ao espaco local
    d = obj.matrix_world.translation - camera.matrix_world.translation
    d.z = 0.0
    d_local = obj.matrix_world.to_3x3().inverted() @ d.normalized()
    ang_tras = math.atan2(d_local.y, d_local.x)

    def dif(a, b):
        return abs((a - b + math.pi) % (2 * math.pi) - math.pi)

    bm = bmesh.new()
    bm.from_mesh(me)
    for e in bm.edges:
        e.seam = False
    # corpos de revolucao: aneis com >= 24 vertices no mesmo raio (tubo e bocal);
    # em cada um, o angulo de vertice mais proximo de "atras" recebe a seam
    por_raio = {}
    for v in bm.verts:
        r = round(math.hypot(v.co.x, v.co.y), 2)
        if r > 0.01:
            por_raio.setdefault(r, set()).add(round(math.atan2(v.co.y, v.co.x), 4))
    phi_raio = {r: min(angs, key=lambda x: dif(x, ang_tras))
                for r, angs in por_raio.items() if len(angs) >= 24}

    def na_linha(v):
        r = round(math.hypot(v.co.x, v.co.y), 2)
        if r <= 0.01:
            return True                       # ponta do cone
        return r in phi_raio and dif(math.atan2(v.co.y, v.co.x), phi_raio[r]) < 0.01

    n_vivas = n_tras = 0
    for e in bm.edges:
        a, b = e.verts
        if e.calc_face_angle(0.0) > math.radians(60):
            e.seam = True
            n_vivas += 1
        elif na_linha(a) and na_linha(b) and abs(a.co.z - b.co.z) > 1e-4:
            e.seam = True                     # aresta longitudinal atras
            n_tras += 1
    bm.to_mesh(me)
    bm.free()
    return dict(angulo_tras_graus=round(math.degrees(ang_tras), 1), seams_vivas=n_vivas,
                seams_tras=n_tras)


def preparar_uv(obj, metodo):
    """Cria o mapa UV_AC05 por 'cubo' (Cube Projection) ou 'smart' (Smart UV
    Project). Retorna dict com escala UV->unidades da cena e metrica de
    distorcao (fracao de faces com densidade de texel entre 0.5x e 2x da mediana)."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    me = obj.data
    if metodo == "seam":
        info_seam = marcar_seams_atras(obj, bpy.data.objects["Cam_Principal"])
        print("[AC05] seams do foguete:", info_seam)
    for l in list(me.uv_layers):
        me.uv_layers.remove(l)
    me.uv_layers.new(name=UV_NOME)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    if metodo == "cubo":
        # cube_size ~ maior dimensao do objeto: UV cabe em ~0..1 no UV Editor
        tam = max(obj.dimensions)
        bpy.ops.uv.cube_project(cube_size=tam, correct_aspect=True,
                                clip_to_bounds=False, scale_to_bounds=False)
    elif metodo == "seam":
        # unwrap respeitando os seams marcados por marcar_seams_atras()
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method="CONFORMAL", margin=0.02)
        bpy.ops.uv.average_islands_scale()
        bpy.ops.uv.pack_islands(margin=0.02, rotate=False)
    else:
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),
                                 island_margin=0.02, area_weight=0.0,
                                 correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    # densidade de texel por face: area UV / area no mundo
    esc = obj.matrix_world.to_scale()[0]
    uv = me.uv_layers[UV_NOME].data
    area_mundo = area_uv = 0.0
    dens = []
    for p in me.polygons:
        pts = [uv[i].uv for i in p.loop_indices]
        a_uv = 0.5 * abs(sum(pts[i].x * pts[(i + 1) % len(pts)].y
                             - pts[(i + 1) % len(pts)].x * pts[i].y
                             for i in range(len(pts))))
        a_w = p.area * esc * esc
        area_mundo += a_w
        area_uv += a_uv
        if a_w > 1e-9 and a_uv > 1e-12:
            dens.append(a_uv / a_w)
    dens.sort()
    mediana = dens[len(dens) // 2]
    ok = sum(1 for d in dens if 0.5 * mediana <= d <= 2.0 * mediana) / len(dens)
    return dict(uv_para_cena=math.sqrt(area_mundo / area_uv),
                faces_ok=round(ok, 3), n_faces=len(me.polygons), metodo=metodo)


# --------------------------------------------------------------------------
# Materiais
# --------------------------------------------------------------------------
def novo_material(nome):
    antigo = bpy.data.materials.get(nome)
    if antigo:
        bpy.data.materials.remove(antigo)
    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    saida = nt.nodes.new("ShaderNodeOutputMaterial")
    saida.location = (700, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (400, 0)
    nt.links.new(bsdf.outputs["BSDF"], saida.inputs["Surface"])
    return mat, nt, bsdf


def no_imagem(nt, caminho, nome, dados, vetor, loc):
    """Image Texture. dados=True -> Non-Color (rugosidade/normal); False -> sRGB."""
    img = bpy.data.images.load(caminho, check_existing=True)
    img.name = nome
    img.colorspace_settings.name = "Non-Color" if dados else "sRGB"
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = img
    n.label = nome
    n.location = loc
    n.interpolation = "Linear"
    n.extension = "REPEAT"
    nt.links.new(vetor, n.inputs["Vector"])
    return n


def vetor_uv(nt, escala):
    """Texture Coordinate (UV) -> Mapping (escala em X/Y)."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-900, 0)
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.location = (-700, 0)
    mp.vector_type = "POINT"
    mp.inputs["Scale"].default_value = (escala, escala, 1.0)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def normal_map(nt, tex, forca):
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.location = (100, -450)
    nm.space = "TANGENT"
    nm.uv_map = UV_NOME
    nm.inputs["Strength"].default_value = forca
    nt.links.new(tex.outputs["Color"], nm.inputs["Color"])
    return nm


def mat_ibmec(nome, cor_rgba):
    mat, nt, b = novo_material(nome)
    mat.diffuse_color = cor_rgba
    b.inputs["Base Color"].default_value = cor_rgba
    b.inputs["Metallic"].default_value = 0.0
    b.inputs["Roughness"].default_value = IBMEC_ROUGH
    return mat


def mat_madeira(escala_uv):
    mat, nt, b = novo_material("MAT_Madeira_PBR")
    vec = vetor_uv(nt, escala_uv / TILE_MADEIRA_M)
    cor = no_imagem(nt, MADEIRA["cor"], "madeira_basecolor", False, vec, (-300, 300))
    rug = no_imagem(nt, MADEIRA["rough"], "madeira_roughness", True, vec, (-300, 0))
    nor = no_imagem(nt, MADEIRA["normal"], "madeira_normal", True, vec, (-300, -300))
    nm = normal_map(nt, nor, MADEIRA_NORMAL_FORCA)
    nt.links.new(cor.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(rug.outputs["Color"], b.inputs["Roughness"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Metallic"].default_value = 0.0
    return mat


def mat_metal(escala_uv):
    mat, nt, b = novo_material("MAT_Metal_Escovado_PBR")
    vec = vetor_uv(nt, escala_uv / TILE_METAL_M)
    cor = no_imagem(nt, METAL["cor"], "metal_basecolor", False, vec, (-300, 300))
    rug = no_imagem(nt, METAL["rough"], "metal_roughness", True, vec, (-500, 0))
    nor = no_imagem(nt, METAL["normal"], "metal_normal", True, vec, (-300, -300))
    # Map Range mantem a rugosidade final dentro de 0.30..0.50
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.location = (-100, 0)
    mr.clamp = True
    mr.inputs["To Min"].default_value = METAL_ROUGH_MIN
    mr.inputs["To Max"].default_value = METAL_ROUGH_MAX
    nm = normal_map(nt, nor, METAL_NORMAL_FORCA)
    nt.links.new(cor.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(rug.outputs["Color"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Metallic"].default_value = 1.0
    return mat


def mat_espelho():
    mat, nt, b = novo_material("MAT_Espelho_PBR")
    mat.diffuse_color = ESPELHO_COR
    b.inputs["Base Color"].default_value = ESPELHO_COR
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = ESPELHO_ROUGH
    return mat


def criar_refletores(raiz):
    """Auxiliar na colecao AC05_Materiais_Texturas: 3 faixas emissivas atras da
    camera, visiveis SOMENTE para raios glossy (reflexos). Nao aparecem na
    imagem, nao projetam sombra e nao iluminam superficies difusas; servem para
    que espelho e metal tenham o que refletir (o mundo e um cinza uniforme)."""
    col = bpy.data.collections.new(COLECAO_AUX)
    raiz.children.link(col)
    mat = bpy.data.materials.new("MAT_Refletor_Emissivo")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = REFLETOR_FORCA
    sai = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], sai.inputs["Surface"])
    for i, x in enumerate((-4.0, 3.0, 10.0)):
        me = bpy.data.meshes.new(f"Refletor_{i+1}")
        h = 4.0
        me.from_pydata([(-1, 0, 0), (1, 0, 0), (1, 0, h), (-1, 0, h)],
                       [], [(0, 1, 2, 3)])
        me.materials.append(mat)
        o = bpy.data.objects.new(f"Refletor_{i+1}", me)
        col.objects.link(o)
        o.location = (x, -16.0, 0.5)
        o.rotation_euler = (0.0, 0.0, math.pi)   # normal virada para +Y (cena)
        o.visible_camera = False
        o.visible_diffuse = False
        o.visible_shadow = False
        o.visible_transmission = False
        o.visible_volume_scatter = False
    return col


def configurar_world():
    """Mantem o fundo cinza da AC04 para camera e luz difusa e usa o HDRI so em
    raios glossy: Mix Shader com fator Light Path > Is Glossy Ray
    (0 = cinza da AC04, 1 = HDRI). A imagem final e a iluminacao difusa dos
    objetos ficam iguais as da AC04; so os reflexos ganham o HDRI."""
    nt = bpy.context.scene.world.node_tree
    cinza = nt.nodes["Background"]
    saida = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputWorld")
    img = bpy.data.images.load(HDRI, check_existing=True)
    img.name = "hdri_studio_small_08"
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = img
    env.location = (-600, -300)
    bg_hdri = nt.nodes.new("ShaderNodeBackground")
    bg_hdri.inputs["Strength"].default_value = HDRI_FORCA
    bg_hdri.location = (-300, -300)
    lp = nt.nodes.new("ShaderNodeLightPath")
    lp.location = (-300, 250)
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.location = (0, 0)
    cinza.location = (-300, 0)
    saida.location = (250, 0)
    nt.links.new(env.outputs["Color"], bg_hdri.inputs["Color"])
    nt.links.new(lp.outputs["Is Glossy Ray"], mix.inputs["Fac"])
    nt.links.new(cinza.outputs["Background"], mix.inputs[1])
    nt.links.new(bg_hdri.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], saida.inputs["Surface"])


def aplicar(nome_obj, mat):
    o = bpy.data.objects[nome_obj]
    o.data.materials.clear()
    o.data.materials.append(mat)
    print(f"[AC05] {mat.name} -> {nome_obj}")


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------
def render_eevee(caminho, w, h, amostras=64):
    s = bpy.context.scene
    for motor in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            s.render.engine = motor
            break
        except TypeError:
            continue
    try:
        s.eevee.taa_render_samples = amostras
    except AttributeError:
        pass
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    s.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    # 1) cena da AC04: abre a AP1, salva copia AC05 e recria as luzes da AC04
    bpy.ops.wm.open_mainfile(filepath=ac04.AP1_BLEND)
    bpy.ops.wm.save_as_mainfile(filepath=DESTINO)   # AP1/AC04 intactos
    raiz = bpy.data.collections["AP1_Ibmec_Conceito"]
    ac04.criar_luzes(raiz)
    cam = bpy.data.objects["Cam_Principal"]
    bpy.context.scene.camera = cam

    # 2) UVs dos objetos texturizados
    uv_comp = preparar_uv(bpy.data.objects["Obj_Computador_Corpo"], "cubo")
    uv_fog = preparar_uv(bpy.data.objects["Obj_Foguete_Corpo"], "seam")
    print("[AC05] UV computador:", uv_comp)
    print("[AC05] UV foguete:   ", uv_fog)

    # 3) materiais
    aplicar("Palavra_Ibmec", mat_ibmec("MAT_Ibmec_PBR", ap1.AZUL_IBMEC))
    aplicar("Palavra_Ponto_i", mat_ibmec("MAT_Ibmec_Ponto_PBR", ap1.LARANJA_IBMEC))
    aplicar("Obj_Computador_Corpo", mat_madeira(uv_comp["uv_para_cena"]))
    aplicar("Obj_Foguete_Corpo", mat_metal(uv_fog["uv_para_cena"]))
    aplicar("Obj_Robo_Corpo", mat_espelho())

    configurar_world()
    if USAR_REFLETORES:
        criar_refletores(raiz)

    # 4) empacota imagens
    bpy.ops.file.pack_all()
    for f in list(bpy.data.fonts):
        if f.users == 0:
            bpy.data.fonts.remove(f)

    # 5) renders (Eevee primeiro, Cycles por ultimo: motor final no .blend)
    t = time.perf_counter()
    render_eevee(os.path.join(SAIDA, "AC05_render_eevee.png"), 1920, 1080, 64)
    t_eevee = time.perf_counter() - t
    t = time.perf_counter()
    ac04.render(os.path.join(SAIDA, "AC05_render.png"), 1920, 1080, 96)
    t_cycles = time.perf_counter() - t
    msg = (f"Eevee 1920x1080: {t_eevee:.1f} s | "
           f"Cycles 1920x1080 96 amostras (CPU, denoise): {t_cycles:.1f} s")
    print("[AC05]", msg)
    with open(os.path.join(SAIDA, "tempo_render.txt"), "w", encoding="utf-8") as fh:
        fh.write(msg + "\n")

    bpy.ops.wm.save_as_mainfile(filepath=DESTINO)
    print("[AC05] salvo:", DESTINO)


if __name__ == "__main__":
    main()
