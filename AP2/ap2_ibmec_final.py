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
# assets (logo + fontes) ficam na AP1 e sao reutilizados pela AP2
ASSETS = os.path.normpath(os.path.join(BASE, "..", "AP1", "assets"))
LOGO_BLENDS = [
    os.path.join(ASSETS, "LOGO_IBMEC_3D.blend"),
    r"C:\Users\mlute\Downloads\LOGO_IBMEC_3D.blend",
]

# Modo da palavra:
#   "A" = logo COMPLETO do arquivo do usuario (usa a fonte Lagu Sans)
#   "B" = malhas do logo ("[" + ponto) + "bmec" recriado em Krub
MODO_LOGO = "B"

# fonte Lagu Sans (usada no modo A) - procura no projeto e no sistema
LAGU_FONTES = [
    os.path.join(ASSETS, "fonts", "Lagu Sans Regular.otf"),
    os.path.join(os.path.expandvars(r"%LOCALAPPDATA%"),
                 "Microsoft", "Windows", "Fonts", "Lagu Sans Regular.otf"),
    r"C:\Windows\Fonts\Lagu Sans Regular.otf",
]

# pose da palavra na cena
PALAVRA_LARGURA = 6.0          # largura-alvo (unidades da cena)
PALAVRA_LOC = (0.0, 0.0, 1.3)

# Animacao (peca final da AP2). Ligada por padrao; desligue com AP2_ANIMAR=0.
# Gera AP2/saida/AP2_animacao.mp4.
ANIMAR = os.environ.get("AP2_ANIMAR", "1") == "1"
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
    palavra.location = PALAVRA_LOC
    aplicar_material(palavra, criar_material("Mat_Ibmec", AZUL_IBMEC,
                                             metallic=0.2, roughness=0.28,
                                             coat=0.6))
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
    mat = bpy.data.materials.new("Mat_Ponto_Ibmec")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = LARANJA_IBMEC
    bsdf.inputs["Roughness"].default_value = 0.4
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = LARANJA_IBMEC
        bsdf.inputs["Emission Strength"].default_value = 0.5
    ponto.data.materials.append(mat)
    ponto.parent = palavra
    ponto.matrix_parent_inverse = palavra.matrix_world.inverted()
    mover_para(ponto, col)
    return ponto


def criar_palavra(col):
    """Palavra Ibmec principal, conforme MODO_LOGO ('A' ou 'B')."""
    if MODO_LOGO.upper() == "A":
        return _palavra_logo_completo(col)
    return _palavra_krub_completa(col)


def _caixa_livro(dims, centro, cor_rgba, nome, bevel=0.02):
    """Caixa (capa/paginas) com escala aplicada, bevel e material proprio."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=centro)
    o = bpy.context.object
    o.name = nome
    o.scale = dims
    set_ativo(o)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bm = _bm_abrir(o)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2,
                    affect="EDGES", clamp_overlap=True)
    _bm_gravar(bm, o)
    aplicar_material(o, criar_material(f"Mat_{nome}", cor_rgba, roughness=0.55))
    return o


def criar_livro(col):
    """Obj_Livro: livro fechado (capa creme + miolo de paginas claro + capa),
    lendo claramente como um livro; serve de pedestal/prop sob a palavra."""
    capa_baixo = _caixa_livro((1.5, 1.05, 0.10), (0, 0, 0.05),
                              CREME, "Livro_CapaBaixo")
    paginas = _caixa_livro((1.40, 0.95, 0.14), (0, 0, 0.17),
                           (0.92, 0.90, 0.82, 1.0), "Livro_Paginas", bevel=0.01)
    capa_cima = _caixa_livro((1.5, 1.05, 0.06), (0, 0, 0.27),
                             CREME, "Livro_CapaCima")

    bpy.ops.object.select_all(action="DESELECT")
    for o in (paginas, capa_cima):
        o.select_set(True)
    capa_baixo.select_set(True)
    bpy.context.view_layer.objects.active = capa_baixo
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "Obj_Livro"

    obj.location = (0.0, -0.55, 0.0)
    obj.rotation_euler = (0, 0, math.radians(-8))   # leve angulo
    mover_para(obj, col)
    return obj


def criar_torre(col):
    """Obj_Torre: cubo alto + inset (janelas) + Array (andares) + antena."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = "Obj_Torre"
    obj.scale = (0.7, 0.7, 1.6)
    set_ativo(obj)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # janelas: inset nas faces laterais
    bm = _bm_abrir(obj)
    laterais = [f for f in bm.faces if abs(f.normal.z) < 0.5]
    if laterais:
        bmesh.ops.inset_individual(bm, faces=laterais, thickness=0.12,
                                   depth=-0.06)
    _bm_gravar(bm, obj)

    # Array vertical (andares) e aplica
    mod = obj.modifiers.new(name="Andares", type="ARRAY")
    mod.count = 4
    mod.relative_offset_displace = (0, 0, 1.03)
    set_ativo(obj)
    bpy.ops.object.modifier_apply(modifier="Andares")

    # antena no topo
    _, _, _, _, _, ztop = _bbox_mundo([obj])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=1.4,
                                        location=(0, 0, ztop + 0.7))
    antena = bpy.context.object
    bpy.ops.object.select_all(action="DESELECT")
    antena.select_set(True)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "Obj_Torre"

    obj.location = (-3.6, 2.2, 0.8)
    obj.rotation_euler = (0, 0, math.radians(18))
    cor(obj, CINZA_AZUL)
    mover_para(obj, col)
    return obj


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

    obj.location = (3.6, 1.0, 1.9)
    obj.rotation_euler = (math.radians(20), 0, math.radians(-15))  # decolagem diagonal
    obj.scale = (1.1, 1.1, 1.1)
    cor(obj, VERMELHO)
    mover_para(obj, col)

    # chama (emissiva) na base - escondida (escala 0) ate a decolagem
    bpy.context.view_layer.update()
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.3, radius2=0.0,
                                    depth=1.1, location=(0, 0, 0))
    chama = bpy.context.object
    chama.name = "Obj_Foguete_Chama"
    chama.data.transform(Matrix.Translation((0, 0, 0.55)))  # apice p/ baixo
    chama.rotation_euler = (math.radians(180), 0, 0)
    set_ativo(chama)
    bpy.ops.object.shade_smooth()
    mat_ch = bpy.data.materials.new("Mat_Chama")
    mat_ch.use_nodes = True
    b = mat_ch.node_tree.nodes.get("Principled BSDF")
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (1.0, 0.45, 0.05, 1.0)
        b.inputs["Emission Strength"].default_value = 8.0
    chama.data.materials.append(mat_ch)
    # posiciona na base do foguete e parenteia
    chama.parent = obj
    chama.matrix_parent_inverse = obj.matrix_world.inverted()
    chama.location = (3.6, 1.0, 0.0)
    chama.scale = (0.0, 0.0, 0.0)     # escondida nos stills
    mover_para(chama, col)

    # fumaca (fake): esfera alongada cinza translucida abaixo da chama
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 0))
    fum = bpy.context.object
    fum.name = "Obj_Foguete_Fumaca"
    set_ativo(fum)
    bpy.ops.object.shade_smooth()
    mat_f = bpy.data.materials.new("Mat_Fumaca")
    mat_f.use_nodes = True
    try:
        mat_f.blend_method = "BLEND"          # Eevee legado
    except (AttributeError, TypeError):
        pass
    bf = mat_f.node_tree.nodes.get("Principled BSDF")
    bf.inputs["Base Color"].default_value = (0.5, 0.5, 0.52, 1.0)
    bf.inputs["Roughness"].default_value = 1.0
    if "Alpha" in bf.inputs:
        bf.inputs["Alpha"].default_value = 0.35
    fum.data.materials.append(mat_f)
    fum.parent = obj
    fum.matrix_parent_inverse = obj.matrix_world.inverted()
    fum.location = (3.6, 1.0, -0.6)
    fum.scale = (0.0, 0.0, 0.0)       # escondida nos stills
    mover_para(fum, col)
    bpy.context.view_layer.update()
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


def criar_planeta(col):
    """Planeta/lua distante ao fundo (dá escala e interesse ao ceu vazio)."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.2, location=(-9.0, 26.0, 9.5))
    p = bpy.context.object
    p.name = "Fundo_Planeta"
    set_ativo(p)
    bpy.ops.object.shade_smooth()
    mat = bpy.data.materials.new("Mat_Planeta")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.12, 0.16, 0.30, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    # textura sutil na superficie
    ntex = nt.nodes.new("ShaderNodeTexNoise")
    ntex.inputs["Scale"].default_value = 3.5
    rmp = nt.nodes.new("ShaderNodeValToRGB")
    rmp.color_ramp.elements[0].color = (0.06, 0.08, 0.18, 1.0)
    rmp.color_ramp.elements[1].color = (0.16, 0.20, 0.36, 1.0)
    nt.links.new(ntex.outputs["Fac"], rmp.inputs["Fac"])
    nt.links.new(rmp.outputs["Color"], bsdf.inputs["Base Color"])
    p.data.materials.append(mat)
    mover_para(p, col)
    return p


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
    # Depth of Field: foco na palavra (fundo/estrelas levemente desfocados)
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = alvo
    cam_data.dof.aperture_fstop = 3.2
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
    scn.timeline_markers.new("Inicio", frame=1)
    scn.timeline_markers.new("Destaque_Ibmec", frame=180)
    scn.timeline_markers.new("Encerramento", frame=FRAME_END)


# --------------------------------------------------------------------------
# Materiais, luzes e render (Eevee) - preview de acabamento
# --------------------------------------------------------------------------
def criar_material(nome, cor, metallic=0.0, roughness=0.5, coat=0.0):
    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = cor
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if coat and "Coat Weight" in bsdf.inputs:      # verniz (clearcoat)
        bsdf.inputs["Coat Weight"].default_value = coat
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = 0.05
    return mat


def aplicar_material(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def criar_material_chao_texturizado():
    """Material do chao com TEXTURA procedural (Noise) na cor e no relevo (Bump)."""
    mat = bpy.data.materials.new("Mat_Chao_Textura")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 12.0
    noise.inputs["Detail"].default_value = 6.0

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.03, 0.035, 0.05, 1.0)   # espacial, escuro
    ramp.color_ramp.elements[1].color = (0.08, 0.09, 0.12, 1.0)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.08
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    # piso "futurista" reflexivo com RUGOSIDADE VARIAVEL (mancha o reflexo)
    rnoise = nt.nodes.new("ShaderNodeTexNoise")
    rnoise.inputs["Scale"].default_value = 3.0
    rnoise.inputs["Detail"].default_value = 2.0
    rramp = nt.nodes.new("ShaderNodeValToRGB")
    rramp.color_ramp.elements[0].color = (0.10, 0.10, 0.10, 1.0)  # bem reflexivo
    rramp.color_ramp.elements[1].color = (0.42, 0.42, 0.42, 1.0)  # mais fosco
    nt.links.new(rnoise.outputs["Fac"], rramp.inputs["Fac"])
    nt.links.new(rramp.outputs["Color"], bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = 0.1
    return mat


def aplicar_materiais(objetos):
    """Atribui materiais (cores da marca) aos objetos da cena.
    A palavra NAO recebe material aqui: usa os materiais originais do logo.
    O livro tambem ja tem materiais proprios (capa/paginas)."""
    aplicar_material(objetos["torre"],
                     criar_material("Mat_Torre", CINZA_AZUL,
                                    metallic=0.2, roughness=0.4))
    aplicar_material(objetos["foguete"],
                     criar_material("Mat_Foguete", VERMELHO, roughness=0.35))

    chao = bpy.data.objects.get("Aux_Chao")
    if chao:
        aplicar_material(chao, criar_material_chao_texturizado())
    mat_bloco = criar_material("Mat_Bloco", BLOCO_COR, roughness=0.7)
    for obj in bpy.data.objects:
        if obj.name.startswith("Aux_Bloco_"):
            aplicar_material(obj, mat_bloco)


def criar_luzes(col):
    """Iluminacao simples de preview (chave + preenchimento)."""
    sol_data = bpy.data.lights.new("Luz_Sol", type="SUN")
    sol_data.energy = 3.5
    sol = bpy.data.objects.new("Luz_Sol", sol_data)
    bpy.context.scene.collection.objects.link(sol)
    sol.rotation_euler = (math.radians(55), math.radians(12), math.radians(35))
    mover_para(sol, col)

    fill_data = bpy.data.lights.new("Luz_Preenchimento", type="AREA")
    fill_data.energy = 400.0
    fill_data.size = 10.0
    fill = bpy.data.objects.new("Luz_Preenchimento", fill_data)
    bpy.context.scene.collection.objects.link(fill)
    fill.location = (5.0, -6.0, 6.0)
    mover_para(fill, col)

    # luz de contorno (rim) azulada atras -> separa objetos do fundo escuro
    rim_data = bpy.data.lights.new("Luz_Contorno", type="AREA")
    rim_data.energy = 900.0
    rim_data.size = 8.0
    rim_data.color = (0.4, 0.6, 1.0)
    rim = bpy.data.objects.new("Luz_Contorno", rim_data)
    bpy.context.scene.collection.objects.link(rim)
    rim.location = (-3.0, 8.0, 5.0)
    rim.rotation_euler = (math.radians(-55), 0.0, math.radians(-20))
    mover_para(rim, col)


def configurar_ceu_espacial():
    """Fundo espacial: gradiente escuro azul-marinho + estrelas procedurais,
    montado nos nos do World."""
    scn = bpy.context.scene
    if scn.world is None:
        scn.world = bpy.data.worlds.new("World")
    world = scn.world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    coord = nt.nodes.new("ShaderNodeTexCoord")

    # --- gradiente vertical (fundo do ceu) ---
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Generated"], sep.inputs["Vector"])
    grad = nt.nodes.new("ShaderNodeValToRGB")
    grad.color_ramp.elements[0].position = 0.0
    grad.color_ramp.elements[0].color = (0.010, 0.014, 0.045, 1.0)  # horizonte
    grad.color_ramp.elements[1].position = 1.0
    grad.color_ramp.elements[1].color = (0.002, 0.003, 0.012, 1.0)  # topo (quase preto)
    nt.links.new(sep.outputs["Z"], grad.inputs["Fac"])

    # --- nebulosa sutil (azul/roxo) ---
    neb = nt.nodes.new("ShaderNodeTexNoise")
    neb.inputs["Scale"].default_value = 2.0
    neb.inputs["Detail"].default_value = 4.0
    nt.links.new(coord.outputs["Generated"], neb.inputs["Vector"])
    neb_ramp = nt.nodes.new("ShaderNodeValToRGB")
    neb_ramp.color_ramp.elements[0].position = 0.40
    neb_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    neb_ramp.color_ramp.elements[1].position = 0.72
    neb_ramp.color_ramp.elements[1].color = (0.10, 0.03, 0.16, 1.0)  # roxo/magenta
    # ponto intermediario azulado
    mid = neb_ramp.color_ramp.elements.new(0.58)
    mid.color = (0.02, 0.04, 0.14, 1.0)
    nt.links.new(neb.outputs["Fac"], neb_ramp.inputs["Fac"])

    base = nt.nodes.new("ShaderNodeMixRGB")
    base.blend_type = "ADD"
    base.inputs["Fac"].default_value = 1.0
    nt.links.new(grad.outputs["Color"], base.inputs["Color1"])
    nt.links.new(neb_ramp.outputs["Color"], base.inputs["Color2"])

    # --- estrelas (noise com corte alto) ---
    mapp = nt.nodes.new("ShaderNodeMapping")
    mapp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    nt.links.new(coord.outputs["Generated"], mapp.inputs["Vector"])
    star_noise = nt.nodes.new("ShaderNodeTexNoise")
    star_noise.inputs["Scale"].default_value = 120.0
    star_noise.inputs["Detail"].default_value = 2.0
    nt.links.new(mapp.outputs["Vector"], star_noise.inputs["Vector"])
    star_ramp = nt.nodes.new("ShaderNodeValToRGB")
    star_ramp.color_ramp.interpolation = "CONSTANT"
    star_ramp.color_ramp.elements[0].position = 0.0
    star_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    star_ramp.color_ramp.elements[1].position = 0.72   # corte alto -> poucas estrelas
    star_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(star_noise.outputs["Fac"], star_ramp.inputs["Fac"])

    # segunda camada de estrelas: maiores, mais raras e mais brilhantes
    star2_noise = nt.nodes.new("ShaderNodeTexNoise")
    star2_noise.inputs["Scale"].default_value = 45.0
    star2_noise.inputs["Detail"].default_value = 2.0
    nt.links.new(mapp.outputs["Vector"], star2_noise.inputs["Vector"])
    star2_ramp = nt.nodes.new("ShaderNodeValToRGB")
    star2_ramp.color_ramp.interpolation = "CONSTANT"
    star2_ramp.color_ramp.elements[0].position = 0.0
    star2_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    star2_ramp.color_ramp.elements[1].position = 0.80   # ainda mais raras
    star2_ramp.color_ramp.elements[1].color = (1.6, 1.7, 2.0, 1.0)  # brilho azulado
    nt.links.new(star2_noise.outputs["Fac"], star2_ramp.inputs["Fac"])

    # estrelas (2 camadas) + fundo -> Background
    estrelas = nt.nodes.new("ShaderNodeMixRGB")
    estrelas.blend_type = "ADD"
    estrelas.inputs["Fac"].default_value = 1.0
    nt.links.new(star_ramp.outputs["Color"], estrelas.inputs["Color1"])
    nt.links.new(star2_ramp.outputs["Color"], estrelas.inputs["Color2"])

    combina = nt.nodes.new("ShaderNodeMixRGB")
    combina.blend_type = "ADD"
    combina.inputs["Fac"].default_value = 1.0
    nt.links.new(base.outputs["Color"], combina.inputs["Color1"])
    nt.links.new(estrelas.outputs["Color"], combina.inputs["Color2"])
    nt.links.new(combina.outputs["Color"], bg.inputs["Color"])


def configurar_render():
    scn = bpy.context.scene
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scn.render.engine = engine
            break
        except TypeError:
            continue
    scn.render.resolution_x = 1280
    scn.render.resolution_y = 720
    scn.render.image_settings.file_format = "PNG"
    # fundo espacial (estrelas + gradiente)
    configurar_ceu_espacial()
    # sombras + reflexos (raytracing no Eevee Next) para o piso reflexivo
    try:
        scn.eevee.use_shadows = True
    except AttributeError:
        pass
    for attr in ("use_raytracing", "use_ssr", "use_ssr_refraction"):
        if hasattr(scn.eevee, attr):
            try:
                setattr(scn.eevee, attr, True)
            except (AttributeError, TypeError):
                pass
    configurar_bloom()


def configurar_bloom():
    """Compositor: bloom (Glare) + color grading (contraste/saturacao) +
    vinheta (escurece as bordas)."""
    scn = bpy.context.scene
    scn.use_nodes = True
    nt = scn.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")

    glare = nt.nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.quality = "HIGH"
    glare.threshold = 0.75
    if hasattr(glare, "mix"):
        glare.mix = 0.0
    nt.links.new(rl.outputs["Image"], glare.inputs["Image"])

    # color grading: leve contraste + saturacao
    bc = nt.nodes.new("CompositorNodeBrightContrast")
    bc.inputs["Contrast"].default_value = 8.0
    nt.links.new(glare.outputs["Image"], bc.inputs["Image"])
    hsv = nt.nodes.new("CompositorNodeHueSat")
    if "Saturation" in hsv.inputs:
        hsv.inputs["Saturation"].default_value = 1.12
    nt.links.new(bc.outputs["Image"], hsv.inputs["Image"])

    # vinheta: mascara elipse borrada -> multiplica a imagem
    mask = nt.nodes.new("CompositorNodeEllipseMask")
    mask.width = 0.9
    mask.height = 0.9
    blur = nt.nodes.new("CompositorNodeBlur")
    blur.filter_type = "GAUSS"
    blur.size_x = 200
    blur.size_y = 200
    blur.use_relative = False
    nt.links.new(mask.outputs["Mask"], blur.inputs["Image"])
    # remapeia a mascara para nao escurecer demais o centro (0.55..1.0)
    mapv = nt.nodes.new("CompositorNodeMapValue")
    mapv.size = [0.45]
    mapv.use_min = True
    mapv.min = [0.55]
    mapv.offset = [0.55]
    nt.links.new(blur.outputs["Image"], mapv.inputs["Value"])
    mult = nt.nodes.new("CompositorNodeMixRGB")
    mult.blend_type = "MULTIPLY"
    mult.inputs[0].default_value = 1.0          # Fac
    nt.links.new(hsv.outputs["Image"], mult.inputs[1])
    nt.links.new(mapv.outputs["Value"], mult.inputs[2])

    comp = nt.nodes.new("CompositorNodeComposite")
    nt.links.new(mult.outputs["Image"], comp.inputs["Image"])


def render_para(caminho):
    bpy.context.scene.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


def render_entregaveis(cam, alvo, objetos):
    """Renderiza o enquadramento principal + 1 close por objeto autoral."""
    os.makedirs(SAIDA, exist_ok=True)
    # 1) enquadramento principal (camera ja posicionada)
    render_para(os.path.join(SAIDA, "enquadramento_principal.png"))

    # 2) closes: reaponta o alvo e aproxima a camera de cada objeto
    loc_cam_orig = cam.location.copy()
    loc_alvo_orig = alvo.location.copy()
    closes = [
        ("obj_livro.png", objetos["livro"]),
        ("obj_torre.png", objetos["torre"]),
        ("obj_foguete.png", objetos["foguete"]),
    ]
    for arquivo, obj in closes:
        centro = obj.matrix_world.translation
        alvo.location = centro
        cam.location = centro + Vector((0.0, -6.0, 2.2))
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
        BASE, "..", "obsidian-CG_26.2_8001", "4-AP2"))
    if not os.path.isdir(vault_topico):
        return
    destino = os.path.join(vault_topico, "img")
    os.makedirs(destino, exist_ok=True)
    n = 0
    for nome in sorted(os.listdir(SAIDA)):
        if nome.endswith(".png"):
            shutil.copy2(os.path.join(SAIDA, nome), os.path.join(destino, nome))
            n += 1
    print(f"[AP2] {n} figuras sincronizadas para o vault Obsidian (4-AP2/img).")


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
    destino = os.path.join(SAIDA, f"AP2_{AUTOR}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=destino)
    print(f"[AP2] Arquivo salvo em: {destino}")


# --------------------------------------------------------------------------
# Animacao (preview) + render de video
# --------------------------------------------------------------------------
def _key(obj, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        obj.location = loc
        obj.keyframe_insert("location", frame=frame)
    if rot is not None:
        obj.rotation_euler = rot
        obj.keyframe_insert("rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert("scale", frame=frame)


def animar_cena(cam, palavra, foguete):
    """Keyframes reusando os 3 momentos do storyboard. As poses FINAIS
    coincidem com a cena estatica (o ultimo frame == enquadramento hero)."""
    dot = bpy.data.objects.get("Palavra_Ponto_i")
    blocos = [o for o in bpy.data.objects if o.name.startswith("Aux_Bloco_")]

    # Camera: push-in (parte mais afastada/baixa -> enquadramento final)
    fim_cam = cam.location.copy()
    _key(cam, 1, loc=fim_cam + Vector((0.0, -4.0, -1.6)))
    _key(cam, FRAME_END, loc=fim_cam)

    # Blocos: caem e se assentam (escalonado no tempo)
    for i, b in enumerate(blocos):
        rest = b.location.copy()
        rr = b.rotation_euler.copy()
        f0 = 1 + i * 8
        _key(b, f0, loc=rest + Vector((0, 0, 4.0 + 0.5 * i)),
             rot=(rr.x, rr.y, rr.z + math.radians(120)))
        _key(b, f0 + 70, loc=rest, rot=(rr.x, rr.y, rr.z))

    # Palavra: sobe + scale-in, com "pulso" ao completar (sincronizado c/ o pingo)
    rest_loc = palavra.location.copy()
    _key(palavra, 90, loc=rest_loc + Vector((0, 0, -1.1)),
         scale=(0.15, 0.15, 0.15))
    _key(palavra, 190, loc=rest_loc, scale=(1.0, 1.0, 1.0))
    _key(palavra, 202, loc=rest_loc, scale=(1.05, 1.05, 1.05))  # pulso
    _key(palavra, 214, loc=rest_loc, scale=(1.0, 1.0, 1.0))

    # Ponto do 'i': cai e encaixa com overshoot (bounce) + flash de emissao
    if dot:
        rd = dot.location.copy()
        rest_scale = dot.scale.copy()
        _key(dot, 150, loc=rd + Vector((0, 0, 2.5)), scale=rest_scale)
        _key(dot, 198, loc=rd + Vector((0, 0, -0.06)),
             scale=rest_scale * 1.18)             # squash no impacto
        _key(dot, 212, loc=rd, scale=rest_scale)
        _flash_emissao(dot, "Mat_Ponto_Ibmec", base=0.5, pico=6.0,
                       f_ini=196, f_pico=202, f_fim=214)

    # Foguete: decola (sobe acelerando + leve giro)
    rf = foguete.location.copy()
    rrf = foguete.rotation_euler.copy()
    _key(foguete, 280, loc=rf, rot=rrf)
    _key(foguete, FRAME_END, loc=rf + Vector((0.5, 0.0, 8.0)),
         rot=(rrf.x, rrf.y, rrf.z + math.radians(25)))

    # Chama: aparece na ignicao e cresce (escala 0 -> cheia), com flicker
    chama = bpy.data.objects.get("Obj_Foguete_Chama")
    if chama:
        _key(chama, 270, scale=(0.0, 0.0, 0.0))
        _key(chama, 292, scale=(1.0, 1.0, 1.3))
        _key(chama, 320, scale=(0.9, 0.9, 1.5))
        _key(chama, FRAME_END, scale=(1.0, 1.0, 1.4))

    # Fumaca: cresce e alonga durante a subida
    fum = bpy.data.objects.get("Obj_Foguete_Fumaca")
    if fum:
        _key(fum, 272, scale=(0.0, 0.0, 0.0))
        _key(fum, 300, scale=(1.2, 1.2, 2.2))
        _key(fum, FRAME_END, scale=(1.6, 1.6, 3.4))


def _flash_emissao(obj, mat_nome, base, pico, f_ini, f_pico, f_fim):
    """Anima a forca de emissao do material (flash)."""
    mat = bpy.data.materials.get(mat_nome)
    if not mat or not mat.use_nodes:
        return
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf or "Emission Strength" not in bsdf.inputs:
        return
    inp = bsdf.inputs["Emission Strength"]
    for fr, val in ((f_ini, base), (f_pico, pico), (f_fim, base)):
        inp.default_value = val
        inp.keyframe_insert("default_value", frame=fr)


def configurar_video():
    scn = bpy.context.scene
    scn.render.resolution_x = VIDEO_LARGURA
    scn.render.resolution_y = VIDEO_ALTURA
    scn.render.fps = FPS
    scn.frame_start = 1
    scn.frame_end = FRAME_END
    try:
        scn.eevee.taa_render_samples = VIDEO_SAMPLES
    except AttributeError:
        pass
    scn.render.image_settings.file_format = "FFMPEG"
    scn.render.ffmpeg.format = "MPEG4"
    scn.render.ffmpeg.codec = "H264"
    scn.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scn.render.ffmpeg.ffmpeg_preset = "GOOD"
    try:
        scn.render.ffmpeg.audio_codec = "NONE"
    except AttributeError:
        pass
    scn.render.filepath = os.path.join(SAIDA, "AP2_animacao.mp4")


def render_animacao():
    print(f"[AP1] Renderizando animacao {FRAME_END} frames "
          f"({VIDEO_LARGURA}x{VIDEO_ALTURA}) - pode levar minutos...")
    bpy.ops.render.render(animation=True)
    print("[AP2] Animacao salva em AP2/saida/AP2_animacao.mp4")


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
    livro = criar_livro(col_objetos)
    torre = criar_torre(col_objetos)
    foguete = criar_foguete(col_objetos)
    criar_auxiliares(col_aux)
    criar_planeta(col_aux)
    cam, alvo = criar_camera(raiz, alvo_loc=(0.0, 0.0, 2.0))

    col_luzes = nova_colecao("Luzes", raiz)
    criar_luzes(col_luzes)
    aplicar_materiais({"palavra": palavra, "livro": livro, "torre": torre,
                       "foguete": foguete})

    configurar_render()
    # 1) stills (pose estatica = enquadramento hero), antes de inserir keyframes
    render_entregaveis(cam, alvo, {"livro": livro, "torre": torre,
                                   "foguete": foguete})
    sincronizar_obsidian()

    # 2) animacao (preview da AP2), opcional
    if ANIMAR:
        animar_cena(cam, palavra, foguete)
        configurar_video()
        render_animacao()
        bpy.context.scene.frame_set(FRAME_END)  # abre no frame hero

    salvar_blend()

    print("=" * 70)
    print("Cena AP1 construida: colecao AP1_Ibmec_Conceito, palavra + 3 objetos,")
    print(f"camera principal e timeline {FRAME_END} frames @ {FPS} fps.")
    extra = " + AP2_animacao.mp4" if ANIMAR else ""
    print(f"Entregaveis (4 PNGs + .blend{extra}) em AP1/saida/.")
    print("=" * 70)


if __name__ == "__main__":
    main()
