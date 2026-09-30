"""
AP1 - Computacao Grafica | Cena-conceito 3D "Ibmec - Construindo o Futuro"
Blender 4.5 LTS  (modulo bpy)

Constroi programaticamente a cena-conceito da AP1:
  - Colecao principal AP1_Ibmec_Conceito (com subcolecoes Palavra/Objetos/Auxiliares)
  - A palavra "Ibmec" como elemento visual principal (texto -> malha, extrusao+bevel)
  - Exatamente 3 objetos autorais modelados a partir de primitivas + modificadores:
        Obj_Livro   (educacao/conhecimento)
        Obj_Torre   (solidez/construcao)
        Obj_Foguete (futuridade/empreendedorismo)
  - Elementos auxiliares (chao + blocos de "construcao")
  - Transformacoes intencionais de location/rotation/scale
  - Camera principal (Cam_Principal) com constraint Track To mirando a palavra
  - Timeline planejada: 15 s @ 24 fps = 360 frames, com 3 marcadores de storyboard
  - Render solid (Workbench) das 4 imagens entregaveis + salvamento do .blend

NAO faz (fica para a AP2): animacao por keyframes, iluminacao, materiais, texturas,
render final em Eevee/Cycles.

Como executar:
    # GUI: aba Scripting -> abrir este arquivo -> Run Script
    # Headless:
    blender --background --python AP1/ap1_ibmec_conceito.py

Saida: AP1/saida/AP1_<AUTOR>.blend  e  4 PNGs (enquadramento + 3 objetos).
"""

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Vector

# --------------------------------------------------------------------------
# Configuracao (edite AUTOR com seu nome, ex.: "JoaoSilva")
# --------------------------------------------------------------------------
AUTOR = "MichelLutegar"

# Fonte da marca Ibmec: Krub (Google Fonts). Procura em varios locais e usa
# a primeira que existir; se nenhuma for achada, mantem a fonte padrao.
FONTES_IBMEC = [
    os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"),
                 "Microsoft", "Windows", "Fonts", "Krub-SemiBold.ttf"),
    os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"),
                 "Microsoft", "Windows", "Fonts", "Krub-Bold.ttf"),
    os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"),
                 "Microsoft", "Windows", "Fonts", "Krub-Regular.ttf"),
    r"C:\Windows\Fonts\Krub-SemiBold.ttf",
    r"C:\Windows\Fonts\Krub-Regular.ttf",
]

FPS = 24
DURACAO_S = 15
FRAME_END = FPS * DURACAO_S  # 360

AQUI = os.path.dirname(os.path.abspath(bpy.data.filepath)) if bpy.data.filepath else None
# Quando rodado por --python, __file__ aponta para este script:
try:
    BASE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE = os.getcwd()
SAIDA = os.path.join(BASE, "saida")

AZUL_IBMEC = (0.02, 0.04, 0.12, 1.0)   # azul-marinho da marca (~ #1B2A4E)
LARANJA_IBMEC = (0.95, 0.48, 0.03, 1.0)  # laranja do ponto do "i" (~ #F2A007)
CREME = (0.90, 0.86, 0.74, 1.0)
CINZA_AZUL = (0.35, 0.42, 0.52, 1.0)
VERMELHO = (0.75, 0.10, 0.10, 1.0)
BRANCO = (0.92, 0.92, 0.92, 1.0)
CHAO_COR = (0.15, 0.16, 0.19, 1.0)
BLOCO_COR = (0.45, 0.47, 0.52, 1.0)


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def limpar_cena():
    """Remove todos os objetos e datablocks orfaos para comecar limpo."""
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)
    # limpa meshes/curvas/cameras orfas
    for bloco in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras):
        for d in list(bloco):
            if d.users == 0:
                bloco.remove(d)


def nova_colecao(nome, pai):
    col = bpy.data.collections.new(nome)
    pai.children.link(col)
    return col


def mover_para(obj, col):
    """Garante que obj esteja SOMENTE na colecao col."""
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def cor(obj, rgba):
    obj.color = rgba  # usado pelo Workbench com color_type='OBJECT'


def set_ativo(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def _bm_abrir(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def _bm_gravar(bm, obj):
    bm.normal_update()
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


# --------------------------------------------------------------------------
# Construcao da cena
# --------------------------------------------------------------------------
# Opcao B: importa as MALHAS reais do logo (o "[" e o ponto laranja) e
# recria o "bmec" em Krub (a fonte Lagu Sans do arquivo original nao existe
# nesta maquina). As malhas do logo estao no plano XY (altura em Y, rot 0);
# o texto Krub e' criado na mesma orientacao para tudo ficar coplanar.
LOGO_MESHES = ["IBMEC_I", "IBMEC_Serifas_b", "IBMEC_Esfera"]
LOGO_BLENDS = [
    os.path.join(BASE, "assets", "LOGO_IBMEC_3D.blend"),
    r"C:\Users\mlute\Downloads\LOGO_IBMEC_3D.blend",
]

# Modo da palavra:
#   "A" = logo COMPLETO do arquivo do usuario (usa a fonte Lagu Sans)
#   "B" = malhas do logo ("[" + ponto) + "bmec" recriado em Krub
MODO_LOGO = "B"

# fonte Lagu Sans (usada no modo A) - procura no projeto e no sistema
LAGU_FONTES = [
    os.path.join(BASE, "assets", "fonts", "Lagu Sans Regular.otf"),
    os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"),
                 "Microsoft", "Windows", "Fonts", "Lagu Sans Regular.otf"),
    r"C:\Windows\Fonts\Lagu Sans Regular.otf",
]

# pose da palavra na cena
PALAVRA_LARGURA = 6.0          # largura-alvo (unidades da cena)
PALAVRA_LOC = (0.0, 0.0, 1.3)

# Animacao (preview da AP2). Ative com a variavel de ambiente AP1_ANIMAR=1
# ou trocando para True aqui. Gera AP1/saida/AP1_animacao.mp4.
ANIMAR = os.environ.get("AP1_ANIMAR", "0") == "1"
VIDEO_LARGURA, VIDEO_ALTURA = 1280, 720
VIDEO_SAMPLES = 32


def _bbox_mundo(objs):
    cantos = []
    for o in objs:
        cantos += [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [c.x for c in cantos]
    ys = [c.y for c in cantos]
    zs = [c.z for c in cantos]
    return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def _texto_krub_bmec():
    """Cria 'bmec' em Krub (extrusao+bevel) e converte em malha, alinhado
    a esquerda/baseline (mesma orientacao das malhas do logo: altura em Y)."""
    curva = bpy.data.curves.new(name="bmec", type="FONT")
    curva.body = "bmec"
    for caminho in FONTES_IBMEC:
        if os.path.isfile(caminho):
            curva.font = bpy.data.fonts.load(caminho)
            print(f"[AP1] Fonte do 'bmec': {os.path.basename(caminho)}")
            break
    curva.extrude = 0.27          # ~ mesma profundidade das malhas do logo
    curva.bevel_depth = 0.02
    curva.bevel_resolution = 2
    curva.align_x = "LEFT"
    curva.align_y = "BOTTOM_BASELINE"
    obj = bpy.data.objects.new("bmec", curva)
    bpy.context.scene.collection.objects.link(obj)
    set_ativo(obj)
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def _achar_logo_blend():
    origem = next((p for p in LOGO_BLENDS if os.path.isfile(p)), None)
    if origem is None:
        raise FileNotFoundError("LOGO_IBMEC_3D.blend nao encontrado.")
    return origem


def _importar_objs(origem, nomes):
    with bpy.data.libraries.load(origem, link=False) as (df, dt):
        disp = list(df.objects)
        dt.objects = [n for n in nomes if n in disp]
    return [o for o in dt.objects if o is not None]


def _juntar_e_posicionar(objs, ativo, col):
    """Junta objs (ativo base), centraliza, escala p/ largura-alvo e posiciona.
    Objetos ja devem estar EM PE (altura em Z, de frente pra -Y)."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = ativo
    bpy.ops.object.join()
    palavra = bpy.context.object
    palavra.name = "Palavra_Ibmec"

    x0, x1, y0, y1, z0, z1 = _bbox_mundo([palavra])
    centro = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    escala = PALAVRA_LARGURA / (x1 - x0 or 1.0)
    palavra.data.transform(Matrix.Translation(-centro))
    palavra.data.transform(Matrix.Scale(escala, 4))
    palavra.data.update()
    palavra.location = PALAVRA_LOC
    mover_para(palavra, col)
    bpy.context.view_layer.update()
    return palavra


def _palavra_logo_completo(col):
    """MODO A: importa o logo COMPLETO (Text + '[' + serifas + esfera) e
    reaponta o texto para a fonte Lagu Sans local, mantendo o design oficial."""
    origem = _achar_logo_blend()
    print(f"[AP1] (Modo A) Importando logo completo de: {origem}")
    objs = _importar_objs(origem, LOGO_MESHES + ["Text"])
    if not objs:
        raise RuntimeError("Nenhum objeto do logo foi importado.")
    for o in objs:
        col.objects.link(o)
    bpy.context.view_layer.update()

    lagu = next((p for p in LAGU_FONTES if os.path.isfile(p)), None)
    if lagu is None:
        raise FileNotFoundError(
            "Fonte Lagu Sans nao encontrada (assets/fonts ou sistema).")
    font_lagu = bpy.data.fonts.load(lagu)
    print(f"[AP1] Fonte do texto (Lagu Sans): {os.path.basename(lagu)}")

    base = None
    for o in objs:
        if o.type == "FONT":
            o.data.font = font_lagu
            for attr in ("font_bold", "font_italic", "font_bold_italic"):
                if getattr(o.data, attr, None) is not None:
                    setattr(o.data, attr, font_lagu)
            bpy.ops.object.select_all(action="DESELECT")
            set_ativo(o)
            bpy.ops.object.convert(target="MESH")
            o = bpy.context.object
        if o.name.split(".")[0] == "IBMEC_I":
            base = o
    objs = [bpy.data.objects[o.name] if o.name in bpy.data.objects else o
            for o in objs]
    return _juntar_e_posicionar(objs, base or objs[0], col)


def _palavra_meshes_krub(col):
    """MODO B: malhas do logo ('[' + ponto) + 'bmec' recriado em Krub."""
    origem = _achar_logo_blend()
    print(f"[AP1] (Modo B) Importando malhas do logo de: {origem}")
    malhas = _importar_objs(origem, LOGO_MESHES)
    if not malhas:
        raise RuntimeError("Nenhuma malha do logo foi importada.")
    for o in malhas:
        col.objects.link(o)
    bpy.context.view_layer.update()

    ref = {o.name.split(".")[0]: o for o in malhas}
    bracket = [ref[k] for k in ("IBMEC_I", "IBMEC_Serifas_b") if k in ref]
    mat_navy = bracket[0].active_material if bracket else None

    bx0, bx1, by0, by1, bz0, bz1 = _bbox_mundo(bracket or malhas)
    altura = bz1 - bz0
    prof_c = (by0 + by1) / 2.0
    base_z = bz0

    bmec = _texto_krub_bmec()
    bmec.rotation_euler = (math.radians(90), 0.0, 0.0)
    bpy.context.view_layer.update()
    kx0, kx1, ky0, ky1, kz0, kz1 = _bbox_mundo([bmec])
    sf = altura / (kz1 - kz0)
    bmec.scale = (sf, sf, sf)
    bpy.context.view_layer.update()
    kx0, kx1, ky0, ky1, kz0, kz1 = _bbox_mundo([bmec])
    gap = 0.14 * altura
    bmec.location = (
        bmec.location.x + (bx1 + gap - kx0),
        bmec.location.y + (prof_c - (ky0 + ky1) / 2.0),
        bmec.location.z + (base_z - kz0),
    )
    if mat_navy:
        bmec.data.materials.clear()
        bmec.data.materials.append(mat_navy)
    bpy.context.view_layer.update()
    return _juntar_e_posicionar(malhas + [bmec], malhas[0], col)


def _palavra_krub_completa(col):
    """MODO B: 'Ibmec' inteiro em Krub (I maiusculo casa com as letras),
    extrusao rasa, azul-marinho, + ponto laranja do 'i'."""
    curva = bpy.data.curves.new(name="Palavra_Ibmec", type="FONT")
    curva.body = "Ibmec"
    for caminho in FONTES_IBMEC:
        if os.path.isfile(caminho):
            curva.font = bpy.data.fonts.load(caminho)
            print(f"[AP1] (Modo B) Fonte: {os.path.basename(caminho)}")
            break
    curva.extrude = 0.05          # profundidade RASA (letras menos fundas)
    curva.bevel_depth = 0.008
    curva.bevel_resolution = 2
    curva.align_x = "CENTER"
    curva.align_y = "BOTTOM_BASELINE"
    obj = bpy.data.objects.new("Palavra_Ibmec", curva)
    bpy.context.scene.collection.objects.link(obj)
    set_ativo(obj)
    bpy.ops.object.convert(target="MESH")
    palavra = bpy.context.object
    palavra.name = "Palavra_Ibmec"

    # levanta (90 X) e aplica a rotacao -> objeto volta a ser identidade
    palavra.rotation_euler = (math.radians(90), 0.0, 0.0)
    set_ativo(palavra)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    # centraliza, escala por largura-alvo e posiciona
    x0, x1, y0, y1, z0, z1 = _bbox_mundo([palavra])
    centro = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    escala = PALAVRA_LARGURA / (x1 - x0 or 1.0)
    palavra.data.transform(Matrix.Translation(-centro))
    palavra.data.transform(Matrix.Scale(escala, 4))
    palavra.data.update()
    # posiciona em X/Y e ASSENTA no chao (base das letras em z=0)
    palavra.location = (PALAVRA_LOC[0], PALAVRA_LOC[1], 0.0)
    bpy.context.view_layer.update()
    _, _, _, _, z0g, _ = _bbox_mundo([palavra])
    palavra.location.z += (0.0 - z0g)
    cor(palavra, AZUL_IBMEC)          # cor via object color (Workbench)
    mover_para(palavra, col)
    bpy.context.view_layer.update()

    _ponto_i(palavra, col)
    return palavra


def _ponto_i(palavra, col):
    """Esfera laranja sobre a haste do 'I' (leftmost), tamanho ~ da haste."""
    x0, x1, y0, y1, z0, z1 = _bbox_mundo([palavra])
    H = z1 - z0
    raio = 0.085 * H
    px = x0 + 0.11 * H          # centro aproximado da haste do "I"
    pz = z1 + raio * 0.35
    py = (y0 + y1) / 2.0
    bpy.ops.mesh.primitive_uv_sphere_add(radius=raio, location=(px, py, pz))
    ponto = bpy.context.object
    ponto.name = "Palavra_Ponto_i"
    set_ativo(ponto)
    bpy.ops.object.shade_smooth()
    cor(ponto, LARANJA_IBMEC)         # ponto laranja (object color)
    ponto.parent = palavra
    ponto.matrix_parent_inverse = palavra.matrix_world.inverted()
    mover_para(ponto, col)
    return ponto


def criar_palavra(col):
    """Palavra Ibmec principal, conforme MODO_LOGO ('A' ou 'B')."""
    if MODO_LOGO.upper() == "A":
        return _palavra_logo_completo(col)
    return _palavra_krub_completa(col)


def _peca_bevel(dims, centro, nome, bevel=0.03, segs=2):
    """Cubo (peca do robo) com escala aplicada e bevel."""
    o = _cubo(dims, centro, nome)
    bm = _bm_abrir(o)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=segs,
                    affect="EDGES", clamp_overlap=True)
    _bm_gravar(bm, o)
    return o


def _cil(radius, depth, centro, nome, eixo="Z"):
    """Cilindro com eixo em X/Y/Z, rotacao aplicada."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth,
                                        location=centro)
    o = bpy.context.object
    o.name = nome
    if eixo == "X":
        o.rotation_euler = (0, math.radians(90), 0)
    elif eixo == "Y":
        o.rotation_euler = (math.radians(90), 0, 0)
    set_ativo(o)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return o


def _peca_rot(dims, centro, nome, rot_deg=(0, 0, 0), bevel=0.06):
    """Cubo com escala + rotacao aplicadas e bevel (bracos inclinados)."""
    o = _cubo(dims, centro, nome)
    o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    set_ativo(o)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    bm = _bm_abrir(o)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2,
                    affect="EDGES", clamp_overlap=True)
    _bm_gravar(bm, o)
    return o


def criar_robo(col):
    """Obj_Robo (grande): robo-mascote de corpo inteiro (pernas/pes, torso com
    painel, ombros, bracos abertos + maos, cabeca com rosto/boca, orelhas e
    antena), por primitivas + bevel + inset + loop cut + join. OLHOS (ciano) e
    EMBLEMA do peito (laranja) sao subpartes coloridas. Tema: IA / inovacao."""
    partes = []
    # pernas + pes
    for lado, dx in (("E", -0.5), ("D", 0.5)):
        partes.append(_peca_bevel((0.55, 0.78, 0.22), (dx, 0.06, 0.12),
                                  f"Robo_Pe{lado}", 0.06))
        partes.append(_peca_bevel((0.34, 0.34, 0.62), (dx, 0, 0.52),
                                  f"Robo_Perna{lado}", 0.10))
    # torso com painel no peito (inset frontal)
    torso = _peca_bevel((1.6, 0.95, 1.55), (0, 0, 1.55), "Robo_Torso", 0.10)
    bm = _bm_abrir(torso)
    frente = [f for f in bm.faces if f.normal.y < -0.6]
    if frente:
        bmesh.ops.inset_individual(bm, faces=frente, thickness=0.20, depth=-0.05)
    _bm_gravar(bm, torso)
    partes.append(torso)
    # ombros (articulacoes)
    partes.append(_cil(0.26, 0.5, (-0.95, 0, 2.05), "Robo_OmbroE", eixo="X"))
    partes.append(_cil(0.26, 0.5, (0.95, 0, 2.05), "Robo_OmbroD", eixo="X"))
    # bracos abertos (inclinados) + maos
    partes.append(_peca_rot((0.32, 0.32, 1.2), (-1.15, 0, 1.5),
                            "Robo_BracoE", rot_deg=(0, -16, 0), bevel=0.10))
    partes.append(_peca_rot((0.32, 0.32, 1.2), (1.15, 0, 1.5),
                            "Robo_BracoD", rot_deg=(0, 16, 0), bevel=0.10))
    partes.append(_peca_bevel((0.42, 0.42, 0.34), (-1.42, 0, 0.9), "Robo_MaoE", 0.14))
    partes.append(_peca_bevel((0.42, 0.42, 0.34), (1.42, 0, 0.9), "Robo_MaoD", 0.14))
    # pescoco + cabeca (rosto por inset)
    partes.append(_cil(0.3, 0.28, (0, 0, 2.48), "Robo_Pescoco", eixo="Z"))
    cabeca = _peca_bevel((1.3, 1.05, 1.05), (0, 0, 3.15), "Robo_Cabeca", 0.16)
    bm = _bm_abrir(cabeca)
    rosto = [f for f in bm.faces if f.normal.y < -0.6]
    if rosto:
        bmesh.ops.inset_individual(bm, faces=rosto, thickness=0.12, depth=-0.05)
    _bm_gravar(bm, cabeca)
    partes.append(cabeca)
    # boca (grelha): caixinha com loop cuts na face
    boca = _cubo((0.6, 0.06, 0.2), (0, -0.53, 2.9), "Robo_Boca")
    bm = _bm_abrir(boca)
    ax = [e for e in bm.edges
          if abs((e.verts[1].co - e.verts[0].co).normalized().x) > 0.9]
    if ax:
        bmesh.ops.subdivide_edges(bm, edges=ax, cuts=3, use_grid_fill=True)
    _bm_gravar(bm, boca)
    partes.append(boca)
    # orelhas laterais
    partes.append(_cil(0.16, 0.22, (-0.73, 0, 3.15), "Robo_OrelhaE", eixo="X"))
    partes.append(_cil(0.16, 0.22, (0.73, 0, 3.15), "Robo_OrelhaD", eixo="X"))
    # antena (haste + esfera)
    partes.append(_cil(0.05, 0.6, (0, 0, 3.98), "Robo_Antena", eixo="Z"))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, 4.32))
    ponta = bpy.context.object
    ponta.name = "Robo_AntenaPonta"
    set_ativo(ponta)
    bpy.ops.object.shade_smooth()
    partes.append(ponta)

    # junta o corpo -> Obj_Robo
    bpy.ops.object.select_all(action="DESELECT")
    for o in partes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = partes[0]
    bpy.ops.object.join()
    robo = bpy.context.object
    robo.name = "Obj_Robo"
    set_ativo(robo)
    bpy.ops.object.shade_flat()
    cor(robo, CINZA_AZUL)

    # OLHOS (ciano) - subparte colorida
    olhos = []
    for i, dx in enumerate((-0.3, 0.3)):
        e = _cil(0.15, 0.12, (dx, -0.52, 3.28), f"Robo_Olho_{i+1}", eixo="Y")
        olhos.append(e)
    bpy.ops.object.select_all(action="DESELECT")
    for e in olhos:
        e.select_set(True)
    bpy.context.view_layer.objects.active = olhos[0]
    bpy.ops.object.join()
    obj_olhos = bpy.context.object
    obj_olhos.name = "Obj_Robo_Olhos"
    set_ativo(obj_olhos)
    bpy.ops.object.shade_smooth()
    cor(obj_olhos, (0.05, 0.85, 1.0, 1.0))   # ciano brilhante

    # EMBLEMA do peito (laranja) - subparte colorida
    emblema = _cubo((0.42, 0.06, 0.42), (0, -0.5, 1.6), "Obj_Robo_Peito")
    emblema.rotation_euler = (0, 0, math.radians(45))
    set_ativo(emblema)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    cor(emblema, LARANJA_IBMEC)

    for sub in (obj_olhos, emblema):
        sub.parent = robo
        sub.matrix_parent_inverse = robo.matrix_world.inverted()
        mover_para(sub, col)

    # ATRAS da palavra "ibmec"; assentado no chao (tamanho moderado)
    robo.scale = (1.1, 1.1, 1.1)
    bpy.context.view_layer.update()
    x0, x1, y0, y1, z0, z1 = _bbox_mundo([robo])
    robo.location.x += (0.0 - (x0 + x1) / 2.0)   # centralizado em X
    robo.location.y += (3.4 - (y0 + y1) / 2.0)   # atras da palavra (y positivo)
    robo.location.z += (0.0 - z0)                # base no chao
    mover_para(robo, col)
    bpy.context.view_layer.update()
    return robo


def _cubo(dims, centro, nome):
    """Cubo com dimensoes (full) e centro dados, escala aplicada."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centro)
    o = bpy.context.object
    o.name = nome
    o.scale = dims
    set_ativo(o)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


def criar_computador(col):
    """Obj_Computador (grande): monitor (moldura com bevel + tela recuada por
    inset) + pe/base + teclado (inset + loop cuts) unidos por join; TELA escura
    e MOUSE como subpartes nomeadas (parenteadas). Composicao de malhas.
    Tema: tecnologia / inovacao / educacao digital."""
    ZM = 2.05  # altura do centro do monitor (origem do conjunto)

    # --- monitor: moldura (bem grande) ---
    moldura = _cubo((3.6, 0.22, 2.35), (0, 0, ZM), "Monitor")
    bm = _bm_abrir(moldura)
    frente = [f for f in bm.faces if f.normal.y < -0.6]
    if frente:                                   # recesso da tela (inset+recuo)
        bmesh.ops.inset_individual(bm, faces=frente, thickness=0.16, depth=-0.09)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.025, segments=2,
                    affect="EDGES", clamp_overlap=True)
    _bm_gravar(bm, moldura)

    # --- pescoco + base ---
    pescoco = _cubo((0.30, 0.26, 0.95), (0, 0.12, 0.50), "Pescoco")
    base = _cubo((1.5, 0.9, 0.10), (0, 0.14, 0.06), "Base")

    # --- teclado: caixa com inset (teclas) + loop cuts (fileiras) ---
    # NA FRENTE do monitor (-Y = lado da camera), como numa mesa
    teclado = _cubo((3.1, 1.3, 0.18), (0, -1.7, 0.09), "Teclado")
    bm = _bm_abrir(teclado)
    topo = [f for f in bm.faces if f.normal.z > 0.6]
    if topo:
        bmesh.ops.inset_individual(bm, faces=topo, thickness=0.08, depth=-0.03)
    arestas_x = [e for e in bm.edges
                 if abs((e.verts[1].co - e.verts[0].co).normalized().x) > 0.9]
    if arestas_x:
        bmesh.ops.subdivide_edges(bm, edges=arestas_x, cuts=4, use_grid_fill=True)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.01, segments=1,
                    affect="EDGES", clamp_overlap=True)
    _bm_gravar(bm, teclado)

    # junta moldura + pescoco + base + teclado -> Obj_Computador
    bpy.ops.object.select_all(action="DESELECT")
    for o in (pescoco, base, teclado):
        o.select_set(True)
    moldura.select_set(True)
    bpy.context.view_layer.objects.active = moldura
    bpy.ops.object.join()
    comp = bpy.context.object
    comp.name = "Obj_Computador"
    set_ativo(comp)
    bpy.ops.object.shade_flat()
    cor(comp, CINZA_AZUL)

    # --- TELA (escura), objeto separado dentro do recesso ---
    tela = _cubo((3.25, 0.05, 2.05), (0, -0.08, ZM), "Obj_Computador_Tela")
    cor(tela, (0.02, 0.03, 0.07, 1.0))

    # --- MOUSE (ao lado do teclado, na frente), com bevel ---
    mouse = _cubo((0.32, 0.48, 0.13), (2.05, -1.7, 0.065), "Obj_Computador_Mouse")
    set_ativo(mouse)
    bm = _bm_abrir(mouse)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.05, segments=3,
                    affect="EDGES", clamp_overlap=True)
    _bm_gravar(bm, mouse)
    bpy.ops.object.shade_smooth()
    cor(mouse, CINZA_AZUL)

    # parenteia tela/mouse ao conjunto (comp ainda na origem de construcao)
    for o in (tela, mouse):
        o.parent = comp
        o.matrix_parent_inverse = comp.matrix_world.inverted()
        mover_para(o, col)

    # pose final (origem em z=ZM -> mantem a altura); a esquerda da palavra
    comp.location = (-4.9, 2.2, ZM)
    comp.rotation_euler = (0, 0, math.radians(22))   # 3/4 para a camera
    mover_para(comp, col)
    return comp


def criar_foguete(col):
    """Obj_Foguete: cilindro (corpo) + cone (ponta) + aletas + Subsurf/Bevel."""
    # corpo (cilindro com bordas chanfradas)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.4, depth=1.8,
                                        location=(0, 0, 0))
    corpo = bpy.context.object
    corpo.name = "Obj_Foguete"

    # ponta (cone) apoiada no topo do corpo (topo do corpo em z=+0.9)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.4, radius2=0.0,
                                    depth=0.7, location=(0, 0, 1.25))
    ponta = bpy.context.object

    # janela/escotilha: inset numa face frontal do corpo
    bm = _bm_abrir(corpo)
    frente = [f for f in bm.faces
              if abs(f.normal.z) < 0.5 and f.normal.y < -0.6
              and -0.2 < f.calc_center_median().z < 0.45]
    if frente:
        bmesh.ops.inset_individual(bm, faces=frente[:1], thickness=0.06,
                                   depth=-0.03)
    _bm_gravar(bm, corpo)

    # bocal (nozzle) na base
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.28, depth=0.3,
                                        location=(0, 0, -1.02))
    bocal = bpy.context.object

    # aletas: 3 cubos finos ao redor da base (bem visiveis)
    aletas = []
    for i in range(3):
        ang = math.radians(120 * i)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.8))
        a = bpy.context.object
        a.scale = (0.05, 0.36, 0.46)
        a.location = (0.42 * math.cos(ang), 0.42 * math.sin(ang), -0.78)
        a.rotation_euler = (0, 0, ang)
        aletas.append(a)

    # junta tudo no corpo
    bpy.ops.object.select_all(action="DESELECT")
    for o in [ponta, bocal] + aletas:
        o.select_set(True)
    corpo.select_set(True)
    bpy.context.view_layer.objects.active = corpo
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "Obj_Foguete"

    # chanfro leve nas arestas (modificador Bevel) + smooth por angulo
    bev = obj.modifiers.new(name="Chanfro", type="BEVEL")
    bev.width = 0.02
    bev.segments = 2
    set_ativo(obj)
    bpy.ops.object.shade_smooth()

    obj.location = (3.9, 0.2, 2.35)  # maior e a frente (profundidade)
    obj.rotation_euler = (math.radians(20), 0, math.radians(-15))  # decolagem diagonal
    obj.scale = (1.5, 1.5, 1.5)
    cor(obj, VERMELHO)
    mover_para(obj, col)
    return obj


def criar_auxiliares(col):
    """Chao + blocos de 'construcao' que sugerem a montagem da palavra."""
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    chao = bpy.context.object
    chao.name = "Aux_Chao"
    cor(chao, CHAO_COR)
    mover_para(chao, col)

    # blocos com tamanhos variados + bevel (menos "cubo generico").
    # Todos FORA do volume das letras: a frente (y negativo) e nas laterais,
    # assentados no chao (nenhum atras da palavra / y positivo).
    blocos = [
        (-4.2, -0.7, 0.24, 0.48),   # lateral esquerda
        (4.1, -0.9, 0.20, 0.40),    # lateral direita
        (-1.6, -1.7, 0.30, 0.60),   # frente esquerda
        (1.8, -1.6, 0.17, 0.34),    # frente direita
        (0.1, -2.1, 0.26, 0.52),    # frente centro
    ]
    for i, (x, y, z, s) in enumerate(blocos, start=1):
        bpy.ops.mesh.primitive_cube_add(size=s, location=(x, y, z))
        b = bpy.context.object
        b.name = f"Aux_Bloco_{i:02d}"
        b.rotation_euler = (0, 0, math.radians(15 * i))
        bev = b.modifiers.new(name="Chanfro", type="BEVEL")
        bev.width = 0.02
        bev.segments = 2
        set_ativo(b)
        bpy.ops.object.shade_flat()
        cor(b, BLOCO_COR)
        mover_para(b, col)



def criar_camera(col, alvo_loc=(0.0, 0.0, 1.3)):
    """Camera principal com Empty-alvo e constraint Track To (pronta p/ AP2)."""
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=alvo_loc)
    alvo = bpy.context.object
    alvo.name = "Alvo_Camera"
    mover_para(alvo, col)

    cam_data = bpy.data.cameras.new("Cam_Principal")
    cam_data.lens = 40
    cam = bpy.data.objects.new("Cam_Principal", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    # 3/4 + leve contra-plongee (mais baixa) -> composicao mais "heroica"
    cam.location = (3.0, -11.5, 3.4)
    trk = cam.constraints.new(type="TRACK_TO")
    trk.target = alvo
    trk.track_axis = "TRACK_NEGATIVE_Z"
    trk.up_axis = "UP_Y"
    mover_para(cam, col)
    bpy.context.scene.camera = cam
    return cam, alvo


def configurar_timeline_e_marcadores():
    scn = bpy.context.scene
    scn.render.fps = FPS
    scn.frame_start = 1
    scn.frame_end = FRAME_END
    # 3 marcadores de storyboard (inicio / destaque / encerramento)
    scn.timeline_markers.clear()
    scn.timeline_markers.new("Inicio", frame=1)          # Quadro 1 (0-3s)
    scn.timeline_markers.new("Transformacao", frame=73)  # Quadro 2 (3-10s)
    scn.timeline_markers.new("Encerramento", frame=241)  # Quadro 3 (10-15s)


# --------------------------------------------------------------------------
# Render da cena-conceito (Workbench / solid) - entrega da AP1
# --------------------------------------------------------------------------
def configurar_workbench():
    """Shading solido (Workbench) com cores por objeto: entrega da AP1 em
    viewport/solid mode (materiais, luz e render final ficam para a AP2)."""
    scn = bpy.context.scene
    scn.render.engine = "BLENDER_WORKBENCH"
    scn.render.resolution_x = 1280
    scn.render.resolution_y = 720
    scn.render.image_settings.file_format = "PNG"
    shd = scn.display.shading
    shd.light = "STUDIO"
    shd.color_type = "OBJECT"
    shd.show_shadows = True
    shd.show_cavity = True


def render_para(caminho):
    bpy.context.scene.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


def render_entregaveis(cam, alvo, objetos):
    """Renderiza o enquadramento principal + 1 close por objeto autoral."""
    os.makedirs(SAIDA, exist_ok=True)
    # 1) enquadramento principal (camera ja posicionada)
    render_para(os.path.join(SAIDA, "enquadramento_principal.png"))

    # 2) closes: mira no centro (bbox) do objeto e aproxima a camera.
    # o robo fica ATRAS da palavra -> camera mais alta/afastada p/ nao ser tapado.
    loc_cam_orig = cam.location.copy()
    loc_alvo_orig = alvo.location.copy()
    closes = [
        ("obj_robo.png", objetos["robo"], Vector((0.0, -8.5, 5.5))),
        ("obj_computador.png", objetos["computador"], Vector((0.0, -9.5, 3.0))),
        ("obj_foguete.png", objetos["foguete"], Vector((0.0, -7.5, 2.5))),
    ]
    for arquivo, obj, offset in closes:
        x0, x1, y0, y1, z0, z1 = _bbox_mundo([obj])
        centro = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        alvo.location = centro
        cam.location = centro + offset
        bpy.context.view_layer.update()
        render_para(os.path.join(SAIDA, arquivo))

    # restaura o enquadramento principal
    cam.location = loc_cam_orig
    alvo.location = loc_alvo_orig
    bpy.context.view_layer.update()


def sincronizar_obsidian():
    """Copia as PNGs para a pasta img/ do topico AP1 no vault, se existir."""
    import shutil
    vault_topico = os.path.normpath(os.path.join(
        BASE, "..", "obsidian-CG_26.2_8001", "3-AP1"))
    if not os.path.isdir(vault_topico):
        return
    destino = os.path.join(vault_topico, "img")
    os.makedirs(destino, exist_ok=True)
    n = 0
    for nome in sorted(os.listdir(SAIDA)):
        if nome.endswith(".png"):
            shutil.copy2(os.path.join(SAIDA, nome), os.path.join(destino, nome))
            n += 1
    print(f"[AP1] {n} figuras sincronizadas para o vault Obsidian (3-AP1/img).")


def _limpar_fontes_orfas():
    """Remove datablocks de fonte sem uso (ex.: Lagu Sans do logo original),
    evitando avisos de 'Unable to pack file' ao salvar."""
    for f in list(bpy.data.fonts):
        if f.users == 0 and not f.use_fake_user:
            try:
                bpy.data.fonts.remove(f)
            except RuntimeError:
                pass


def salvar_blend():
    os.makedirs(SAIDA, exist_ok=True)
    _limpar_fontes_orfas()
    destino = os.path.join(SAIDA, f"AP1_{AUTOR}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=destino)
    print(f"[AP1] Arquivo salvo em: {destino}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("AP1 - Construindo o Futuro (Ibmec) | Blender", bpy.app.version_string)
    print("=" * 70)

    limpar_cena()
    configurar_timeline_e_marcadores()

    raiz = nova_colecao("AP1_Ibmec_Conceito", bpy.context.scene.collection)
    col_palavra = nova_colecao("Palavra", raiz)
    col_objetos = nova_colecao("Objetos", raiz)
    col_aux = nova_colecao("Auxiliares", raiz)

    palavra = criar_palavra(col_palavra)
    robo = criar_robo(col_objetos)
    computador = criar_computador(col_objetos)
    foguete = criar_foguete(col_objetos)
    criar_auxiliares(col_aux)
    cam, alvo = criar_camera(raiz, alvo_loc=(0.0, 0.0, 2.0))  # nao animada

    configurar_workbench()
    render_entregaveis(cam, alvo, {"robo": robo, "computador": computador,
                                   "foguete": foguete})
    sincronizar_obsidian()
    salvar_blend()

    print("=" * 70)
    print("Cena-conceito AP1: colecao AP1_Ibmec_Conceito (palavra + 3 objetos +")
    print(f"auxiliares), camera principal e timeline {FRAME_END} frames @ {FPS} fps.")
    print("Entregaveis (4 PNGs viewport + .blend) em AP1/saida/.")
    print("Animacao/iluminacao/materiais/render final -> AP2.")
    print("=" * 70)


if __name__ == "__main__":
    main()
