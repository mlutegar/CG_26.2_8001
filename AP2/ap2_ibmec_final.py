"""
AP2 - "Ibmec em 15 segundos" (finalizacao).  Script base (versao 2).

NAO recria a cena: abre AC5/AC05_<AUTOR>.blend (so leitura), organiza colecoes,
configura cena/marcadores, anima camera e elementos e salva AP2_<AUTOR>.blend.
Objetos, materiais e UVs vem da AC05. Excecoes criadas aqui (documentadas):
  - Obj_Robo_Cabeca / Obj_Robo_Braco: ilhas soltas da malha do robo separadas
    (mesma malha, mesmo material MAT_Espelho_PBR) para virar a cabeca e acenar;
  - Obj_Foguete_Chama + Mat_Foguete_Chama: chama emissiva;
  - Mat_Obj_Computador_Tela (ja existia, material proprio da tela) ganha emissao animada.

Variaveis de ambiente (todas opcionais):
  AP2_DESTINO       pasta de saida (padrao: pasta AP2/ deste script)
  AP2_RENDER_TESTE  =1  renderiza as 7 previas 960x540 (motor recomendado) em <DESTINO>/saida/previas/
  AP2_RENDER_MOTOR  =1  teste de motor: frames 1/200/300/360 em 1920x1080, Eevee Next x Cycles OptiX
                        (<DESTINO>/saida/teste_motor/, tempos em tempos.csv)
  AP2_RENDER_TEXTURAS =1 recortes Cycles em tamanho real: foguete 270/315/360, computador 1/200/360
                        (<DESTINO>/saida/texturas_movimento/)
  AP2_RENDER_FINAL  =1  renderiza o video .mp4 (H.264) em <DESTINO>/AP2_<AUTOR>.mp4
  AP2_MOTOR         motor do render final/previas: CYCLES ou EEVEE (padrao = MOTOR_FINAL abaixo)
  AP2_FRAMES        "a-b": intervalo do render final (so para testes; padrao 1-360)
  AP2_ESCALA        % da resolucao do render final (padrao 100)
Sem nenhuma flag: apenas gera o .blend. O video NUNCA e renderizado sem AP2_RENDER_FINAL=1.

Executar:
    blender.exe --background --python AP2/ap2_ibmec_final.py
"""
import glob
import math
import os
import sys
import time

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Euler, Matrix, Vector

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BASE)
sys.path.insert(0, os.path.join(REPO, "AP1"))
import ap1_ibmec_conceito as ap1  # noqa: E402  (AUTOR)

AUTOR = ap1.AUTOR
ORIGEM = os.path.join(REPO, "AC5", f"AC05_{AUTOR}.blend")
DESTINO = os.path.abspath(os.environ.get("AP2_DESTINO", BASE))
SAIDA = os.path.join(DESTINO, "saida")
BLEND = os.path.join(DESTINO, f"AP2_{AUTOR}.blend")
VIDEO = os.path.join(DESTINO, f"AP2_{AUTOR}.mp4")
PREVIAS = os.path.join(SAIDA, "previas")
TESTE_MOTOR = os.path.join(SAIDA, "teste_motor")
TEXTURAS = os.path.join(SAIDA, "texturas_movimento")
FRAMES_PREVIA = (1, 72, 140, 200, 240, 300, 360)
FRAMES_MOTOR = (1, 200, 300, 360)
MOTOR_FINAL = "CYCLES"     # recomendado pelo teste de motor (AP2-Iluminacao-Render)

F_INI, F_FIM, FPS = 1, 360, 24
MARCADORES = ((1, "Inicio"), (73, "Desenvolvimento"), (241, "Encerramento"))

# ------------------------------------------------------------------ parametros da animacao
CAM_INI = Vector((-0.8, -21.0, 1.4))     # plano aberto, levemente baixo
CAM_FIM = Vector((0.0, -14.2, 3.0))      # plano de conjunto, Ibmec centralizada
CAM_F_FIM_PUSH = 330                     # push-in 1..330, travada 330..360
ALVO_CAMERA = "Alvo_Camera"              # Track To: empty fixo em (0, 0, 2) (centro da palavra)

ALVO_Z = 1.4                             # alvo da camera sobe de 2.0 p/ 1.4: Ibmec mais centrada na vertical

# foguete: menor (45%), sobe devagar e termina inteiro no terco superior direito do quadro
FOGUETE_ESC = 0.45
FOGUETE_FIM_XZ = (4.2, 3.46)             # posicao final da origem (x, z); y fica em 0.2
FOGUETE_INCLINA = 0.10                   # rad: leve inclinacao p/ +X
FOGUETE_F0, FOGUETE_FA = 270, 306        # partida (ease-in) ate 306; depois velocidade constante ate 360
CHAMA_ESC_FIM = 1.25                     # alongamento final da chama (eixo Z)

# blocos: (x, y) finais; 03, 04 e 05 afastados da palavra (busca em grade, ver verificar_composicao)
BLOCOS_XY = {1: (-4.2, -0.7), 2: (4.1, -0.9), 3: (-3.6, -2.0), 4: (2.0, -3.5), 5: (-4.4, -3.0)}

# iluminacao
RIM = False                              # rim light atras da palavra (avaliado: ver nota do vault)
RIM_ENERGIA = 120.0
HDRI_EEVEE = 0.5                         # intensidade do HDRI no World p/ Eevee (Is Camera Ray)
TELA_MAX = 0.8                           # limite de Emission Strength da tela (sem branco chapado)
TELA_COR = (0.10, 0.36, 1.0, 1.0)
CHAMA_MAX = 1.2                          # limite de Strength da chama
CHAMA_COR = (1.0, 0.36, 0.04, 1.0)
CYCLES_SPP = 64
MB_OBTURADOR = 0.35                      # motion blur (avaliado: ver nota do vault)


# ------------------------------------------------------------------ helpers
def log(*a):
    print("[AP2]", *a)


def kf(owner, prop, frame, value, interp="BEZIER", easing="AUTO", back=None):
    """Define `prop`, insere keyframe em `frame` e fixa interpolacao/easing desse keyframe
    (vale para o trecho que SAI deste keyframe)."""
    setattr(owner, prop, value)
    owner.keyframe_insert(prop, frame=frame)
    path = owner.path_from_id(prop)
    ad = owner.id_data.animation_data
    for fc in ad.action.fcurves:
        if fc.data_path != path:
            continue
        for p in fc.keyframe_points:
            if abs(p.co[0] - frame) < 1e-3:
                p.interpolation = interp
                p.easing = easing
                p.handle_left_type = p.handle_right_type = "AUTO_CLAMPED"
                if back is not None:
                    p.back = back
        fc.update()


def mover_colecao(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def caixa_tela(obj, cena=None):
    """Caixa do objeto projetada na camera: (xmin, ymin, xmax, ymax, prof_min). Coordenadas
    normalizadas do quadro (0..1, y para cima). Usa a bound_box avaliada (conservadora)."""
    cena = cena or bpy.context.scene
    e = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    p = [world_to_camera_view(cena, cena.camera, e.matrix_world @ Vector(c)) for c in e.bound_box]
    return (min(q.x for q in p), min(q.y for q in p), max(q.x for q in p), max(q.y for q in p),
            min(q.z for q in p))


def uniao(caixas):
    return (min(c[0] for c in caixas), min(c[1] for c in caixas),
            max(c[2] for c in caixas), max(c[3] for c in caixas), min(c[4] for c in caixas))


def caixa_palavra(cena=None):
    O = bpy.data.objects
    return uniao([caixa_tela(O["Palavra_Ibmec"], cena), caixa_tela(O["Palavra_Ponto_i"], cena)])


def sobrepoe(a, b, margem=0.0):
    return not (a[2] + margem <= b[0] or b[2] + margem <= a[0] or a[3] + margem <= b[1] or b[3] + margem <= a[1])


def blocos_sobre_palavra(frames, margem=0.008):
    """Lista (frame, bloco, caixa) em que um bloco invade o retangulo da palavra Ibmec."""
    cena = bpy.context.scene
    ruins = []
    for f in frames:
        cena.frame_set(f)
        pal = caixa_palavra(cena)
        for i in range(1, 6):
            c = caixa_tela(bpy.data.objects[f"Aux_Bloco_0{i}"], cena)
            if sobrepoe(c, pal, margem):
                ruins.append((f, f"Aux_Bloco_0{i}", tuple(round(v, 3) for v in c[:4])))
    return ruins


# ------------------------------------------------------------------ 1. colecoes
def organizar_colecoes():
    cols = bpy.data.collections
    raiz = cols["AP1_Ibmec_Conceito"]
    ren = {"Palavra": "Marca", "Objetos": "Objetos_Autorais", "Auxiliares": "Cenario"}
    for velho, novo in ren.items():
        cols[velho].name = novo
    cam = cols.new("Cameras")
    for n in ("Alvo_Camera", "Cam_Principal"):
        mover_colecao(bpy.data.objects[n], cam)
    sc = bpy.context.scene.collection
    for c in [cols["Marca"], cols["Objetos_Autorais"], cols["Cenario"], cam, cols["Luzes"]]:
        if c.name not in sc.children:
            sc.children.link(c)
        if c.name in raiz.children:
            raiz.children.unlink(c)
    cols.remove(raiz)
    log("colecoes:", [c.name for c in sc.children])


# ------------------------------------------------------------------ 2. cena
def configurar_cena():
    s = bpy.context.scene
    s.frame_start, s.frame_end, s.frame_current = F_INI, F_FIM, F_INI
    s.render.fps, s.render.fps_base = FPS, 1.0
    for m in list(s.timeline_markers):
        s.timeline_markers.remove(m)
    for f, n in MARCADORES:
        s.timeline_markers.new(n, frame=f)
    r = s.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.ffmpeg.ffmpeg_preset = "GOOD"
    r.ffmpeg.audio_codec = "NONE"
    r.filepath = VIDEO
    s.cycles.samples = CYCLES_SPP
    s.cycles.use_denoising = True
    s.cycles.denoiser = "OPTIX"
    # limites de emissao (lidos pelo validar_ap2.py)
    s["ap2_limite_tela"] = TELA_MAX
    s["ap2_limite_chama"] = CHAMA_MAX
    # alvo da camera mais baixo -> palavra centrada na vertical
    bpy.data.objects[ALVO_CAMERA].location.z = ALVO_Z


# ------------------------------------------------------------------ 3. robo em partes
def _ilhas(bm):
    bm.verts.ensure_lookup_table()
    visto, ilhas = set(), []
    for v in bm.verts:
        if v.index in visto:
            continue
        pilha, comp = [v], [v]
        visto.add(v.index)
        while pilha:
            x = pilha.pop()
            for e in x.link_edges:
                w = e.other_vert(x)
                if w.index not in visto:
                    visto.add(w.index)
                    pilha.append(w)
                    comp.append(w)
        ilhas.append(comp)
    return ilhas


def _centro(comp):
    xs = [v.co.x for v in comp]
    ys = [v.co.y for v in comp]
    zs = [v.co.z for v in comp]
    return Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)), \
        (min(zs), max(zs))


def separar_parte(corpo, nome, indices_verts, pivo):
    """Cria objeto `nome` com os vertices dados (copia) e remove-os de `corpo`.
    Origem do novo objeto = `pivo` (coords locais do corpo)."""
    me = corpo.data
    bm_novo = bmesh.new()
    bm_novo.from_mesh(me)
    bm_novo.verts.ensure_lookup_table()
    apagar = [v for v in bm_novo.verts if v.index not in indices_verts]
    bmesh.ops.delete(bm_novo, geom=apagar, context="VERTS")
    bmesh.ops.translate(bm_novo, verts=bm_novo.verts, vec=-pivo)
    me_novo = bpy.data.meshes.new(nome)
    bm_novo.to_mesh(me_novo)
    bm_novo.free()
    for m in me.materials:
        me_novo.materials.append(m)
    for p in me_novo.polygons:
        p.use_smooth = True

    bm = bmesh.new()
    bm.from_mesh(me)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.index in indices_verts], context="VERTS")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new(nome, me_novo)
    obj.parent = corpo.parent
    obj.matrix_parent_inverse = corpo.matrix_parent_inverse.copy()
    obj.matrix_basis = corpo.matrix_basis @ Matrix.Translation(pivo)
    for c in corpo.users_collection:
        c.objects.link(obj)
    return obj


def dividir_robo():
    """A malha Obj_Robo_Corpo tem 18 ilhas soltas: cabeca (+orelhas, antena) e bracos.
    Separa cabeca (centro z > 2.55) e o braco +X (centro x > 1.1 e z < 2.3)."""
    corpo = bpy.data.objects["Obj_Robo_Corpo"]
    bm = bmesh.new()
    bm.from_mesh(corpo.data)
    ilhas = _ilhas(bm)
    cabeca, braco = [], []
    for comp in ilhas:
        c, _ = _centro(comp)
        if c.z > 2.55:
            cabeca.append(comp)
        elif c.x > 1.1 and c.z < 2.3:
            braco.append(comp)
    ids_cab = {v.index for comp in cabeca for v in comp}
    ids_bra = {v.index for comp in braco for v in comp}
    # pivos: pescoco (centro xy da cabeca, base da cabeca) e ombro (ilha mais alta do braco)
    todos_cab = [v for comp in cabeca for v in comp]
    cc, (zmin, _) = _centro(todos_cab)
    pivo_cab = Vector((cc.x, cc.y, zmin - 0.05))
    ombro = max(braco, key=lambda comp: _centro(comp)[1][1])
    po, _ = _centro(ombro)
    pivo_bra = Vector((po.x, po.y, po.z))
    bm.free()
    log(f"robo: {len(ilhas)} ilhas; cabeca={len(cabeca)} ilhas, braco={len(braco)} ilhas")

    cab = separar_parte(corpo, "Obj_Robo_Cabeca", ids_cab, pivo_cab)
    # indices do braco nao mudam: separar_parte da cabeca ja removeu verts -> recalcula por posicao
    # (refaz a selecao do braco na malha atual)
    bm = bmesh.new()
    bm.from_mesh(corpo.data)
    ilhas2 = _ilhas(bm)
    ids_bra2 = set()
    for comp in ilhas2:
        c, _ = _centro(comp)
        if c.x > 1.1 and c.z < 2.3:
            ids_bra2 |= {v.index for v in comp}
    bm.free()
    bra = separar_parte(corpo, "Obj_Robo_Braco", ids_bra2, pivo_bra)

    # olhos acompanham a cabeca
    ol = bpy.data.objects["Obj_Robo_Olhos"]
    bpy.context.view_layer.update()   # matrizes atuais antes de reparentar
    mw = ol.matrix_world.copy()
    ol.parent = cab
    ol.matrix_parent_inverse = cab.matrix_world.inverted()
    ol.matrix_basis = mw   # parent inverse = inv(mundo da cabeca) -> mundo = basis
    return cab, bra


# ------------------------------------------------------------------ 4. camera
def animar_camera():
    cam = bpy.data.objects["Cam_Principal"]
    # Track To -> Alvo_Camera (fixo): so a posicao anima; orientacao vem da constraint.
    kf(cam, "location", F_INI, CAM_INI, "BEZIER")                 # ease in
    kf(cam, "location", CAM_F_FIM_PUSH, CAM_FIM, "LINEAR")        # ease out; depois constante
    kf(cam, "location", F_FIM, CAM_FIM, "LINEAR")                 # hero shot travado


# ------------------------------------------------------------------ 5. elementos
def animar_ibmec():
    w = bpy.data.objects["Palavra_Ibmec"]
    z = w.location.z
    # entrada: sobe do chao (z-1.9 -> z) e cresce (0.01 -> 1) de 90 a 190
    kf(w, "scale", 1, (0.01, 0.01, 0.01), "CONSTANT")
    kf(w, "scale", 90, (0.01, 0.01, 0.01), "BACK", "EASE_OUT", back=0.6)
    kf(w, "scale", 190, (1, 1, 1), "SINE", "EASE_IN_OUT")
    # pulso curto 190..214 (1.0 -> 1.07 -> 1.0)
    kf(w, "scale", 200, (1.07, 1.07, 1.07), "SINE", "EASE_IN_OUT")
    kf(w, "scale", 214, (1, 1, 1), "LINEAR")
    kf(w, "scale", F_FIM, (1, 1, 1), "LINEAR")
    kf(w, "location", 1, (w.location.x, w.location.y, z - 1.9), "CONSTANT")
    kf(w, "location", 90, (w.location.x, w.location.y, z - 1.9), "CUBIC", "EASE_OUT")
    kf(w, "location", 190, (w.location.x, w.location.y, z), "LINEAR")
    kf(w, "location", F_FIM, (w.location.x, w.location.y, z), "LINEAR")


def animar_ponto_i():
    d = bpy.data.objects["Palavra_Ponto_i"]
    x, y, z = d.location
    kf(d, "scale", 1, (0.01, 0.01, 0.01), "CONSTANT")
    kf(d, "scale", 140, (0.01, 0.01, 0.01), "LINEAR")
    kf(d, "scale", 150, (1, 1, 1), "LINEAR")
    kf(d, "scale", F_FIM, (1, 1, 1), "LINEAR")
    kf(d, "location", 1, (x, y, z + 4.5), "CONSTANT")
    kf(d, "location", 150, (x, y, z + 4.5), "QUAD", "EASE_IN")         # cai (acelera)
    kf(d, "location", 190, (x, y, z - 0.12), "BACK", "EASE_OUT", back=1.6)  # bate e afunda um pouco
    kf(d, "location", 198, (x, y, z), "LINEAR")                         # encaixa
    kf(d, "location", F_FIM, (x, y, z), "LINEAR")


def animar_blocos():
    lands = [24, 34, 44, 54, 64]
    for i, land in enumerate(lands, 1):
        b = bpy.data.objects[f"Aux_Bloco_0{i}"]
        b.location.x, b.location.y = BLOCOS_XY[i]       # reposicionados: nenhum cobre a Ibmec (190-360)
        x, y, z = b.location
        rz = b.rotation_euler.z
        ini = land - 22
        kf(b, "location", 1, (x, y, z + 9.5), "CONSTANT")
        kf(b, "location", ini, (x, y, z + 9.5), "QUAD", "EASE_IN")
        kf(b, "location", land, (x, y, z), "QUAD", "EASE_OUT")           # quica pequeno
        kf(b, "location", land + 4, (x, y, z + 0.16), "QUAD", "EASE_IN")
        kf(b, "location", land + 8, (x, y, z), "LINEAR")
        kf(b, "location", F_FIM, (x, y, z), "LINEAR")
        kf(b, "rotation_euler", 1, (0, 0, rz + 1.3), "CONSTANT")
        kf(b, "rotation_euler", ini, (0, 0, rz + 1.3), "QUAD", "EASE_OUT")
        kf(b, "rotation_euler", land, (0, 0, rz), "LINEAR")
        kf(b, "rotation_euler", F_FIM, (0, 0, rz), "LINEAR")


def animar_tela():
    mat = bpy.data.materials["Mat_Obj_Computador_Tela"]   # material proprio (nao e MAT_Madeira_PBR)
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Emission Color"].default_value = TELA_COR
    es = b.inputs["Emission Strength"]
    kf(es, "default_value", 1, 0.0, "CONSTANT")
    kf(es, "default_value", 120, 0.0, "LINEAR")
    kf(es, "default_value", 124, TELA_MAX, "LINEAR")           # pisca ao ligar (pico = limite)
    kf(es, "default_value", 127, 0.2 * TELA_MAX, "LINEAR")
    kf(es, "default_value", 132, 0.9 * TELA_MAX, "SINE", "EASE_OUT")
    kf(es, "default_value", 150, 0.8 * TELA_MAX, "LINEAR")
    kf(es, "default_value", F_FIM, 0.8 * TELA_MAX, "LINEAR")


def animar_robo(cab, bra):
    # cabeca: olha a tela do computador (-X) ate 200, depois vira para a palavra/camera (200..230)
    kf(cab, "rotation_euler", 1, (0, 0, -0.65), "BEZIER")
    kf(cab, "rotation_euler", 200, (0, 0, -0.65), "BACK", "EASE_OUT", back=1.2)
    kf(cab, "rotation_euler", 230, (0.14, 0, 0), "LINEAR")
    kf(cab, "rotation_euler", F_FIM, (0.14, 0, 0), "LINEAR")
    # braco: acena 250..290 (levanta, 3 oscilacoes, abaixa)
    A = -2.2
    kf(bra, "rotation_euler", 1, (0, 0, 0), "CONSTANT")
    kf(bra, "rotation_euler", 250, (0, 0, 0), "BACK", "EASE_OUT", back=1.0)
    kf(bra, "rotation_euler", 258, (0, A, 0), "SINE", "EASE_IN_OUT")
    for k, f in enumerate(range(264, 284, 4)):
        kf(bra, "rotation_euler", f, (0, A + (0.38 if k % 2 == 0 else -0.05), 0), "SINE", "EASE_IN_OUT")
    kf(bra, "rotation_euler", 284, (0, A, 0), "BEZIER")
    kf(bra, "rotation_euler", 290, (0, A, 0), "QUAD", "EASE_IN_OUT")
    kf(bra, "rotation_euler", 300, (0, 0, 0), "LINEAR")
    kf(bra, "rotation_euler", F_FIM, (0, 0, 0), "LINEAR")


CHAMA_COMP = 1.5                                  # comprimento da malha (z local: 0 = bocal, -1.5 = ponta)


def _material_chama():
    """Gradiente ao longo do eixo Z do objeto: base amarela clara -> laranja -> vermelho escuro,
    com a emissao e a opacidade caindo na ponta (Emission misturado com Transparent BSDF).
    Um Noise 4D (W por driver = frame) desfaz a regularidade do gradiente (lingua de fogo)."""
    mat = bpy.data.materials.new("Mat_Foguete_Chama")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes, nt.links
    tc = N.new("ShaderNodeTexCoord")
    sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])
    t0 = N.new("ShaderNodeMapRange")                 # z 0 .. -1.5  ->  t 0 .. 1 (0 = bocal, 1 = ponta)
    t0.inputs["From Min"].default_value = 0.0
    t0.inputs["From Max"].default_value = -CHAMA_COMP
    t0.clamp = True
    L.new(sep.outputs["Z"], t0.inputs["Value"])
    nz = N.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 5.0
    nz.inputs["Detail"].default_value = 3.0
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    drv = nt.driver_add('nodes["%s"].inputs["W"].default_value' % nz.name).driver
    drv.type = "SCRIPTED"
    drv.expression = "frame * 0.35"
    mul = N.new("ShaderNodeMath")                    # t' = t + (noise - 0.5) * 0.35 * t   (mais ruido para a ponta)
    mul.operation = "SUBTRACT"
    L.new(nz.outputs["Fac"], mul.inputs[0])
    mul.inputs[1].default_value = 0.5
    mul2 = N.new("ShaderNodeMath")
    mul2.operation = "MULTIPLY"
    L.new(mul.outputs[0], mul2.inputs[0])
    mul2.inputs[1].default_value = 0.35
    mul3 = N.new("ShaderNodeMath")
    mul3.operation = "MULTIPLY"
    L.new(mul2.outputs[0], mul3.inputs[0])
    L.new(t0.outputs[0], mul3.inputs[1])
    add = N.new("ShaderNodeMath")
    add.operation = "ADD"
    add.use_clamp = True
    L.new(t0.outputs[0], add.inputs[0])
    L.new(mul3.outputs[0], add.inputs[1])
    ramp = N.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.0, (1.0, 0.85, 0.25, 1.0)      # nucleo amarelo
    cr.elements[1].position, cr.elements[1].color = 1.0, (0.55, 0.06, 0.01, 1.0)     # ponta vermelha
    e = cr.elements.new(0.4)
    e.color = CHAMA_COR                                                              # laranja no meio
    L.new(add.outputs[0], ramp.inputs["Fac"])
    em = N.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = CHAMA_MAX
    L.new(ramp.outputs["Color"], em.inputs["Color"])
    op = N.new("ShaderNodeMapRange")                 # opacidade: 1 ate t=0.35, cai a 0 em t=1
    op.inputs["From Min"].default_value = 0.35
    op.inputs["From Max"].default_value = 1.0
    op.inputs["To Min"].default_value = 1.0
    op.inputs["To Max"].default_value = 0.0
    op.clamp = True
    L.new(add.outputs[0], op.inputs["Value"])
    tr = N.new("ShaderNodeBsdfTransparent")
    mix = N.new("ShaderNodeMixShader")               # Fac = 1 -> emissao; 0 -> transparente
    L.new(op.outputs[0], mix.inputs[0])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    out = N.new("ShaderNodeOutputMaterial")
    L.new(mix.outputs[0], out.inputs[0])
    return mat


def criar_chama(corpo_foguete):
    # perfil de gota (lathe): larga no bocal (z=0), afina ate a ponta em z=-1.5
    bm = bmesh.new()
    aneis, seg = 14, 24
    rings = []
    for i in range(aneis + 1):
        t = i / aneis
        r = 0.26 * (1.0 - t ** 1.7) ** 0.8 * (1.0 + 0.25 * math.sin(math.pi * min(1.0, t * 1.6)))
        z = -CHAMA_COMP * t
        rings.append([bm.verts.new((max(r, 0.004) * math.cos(2 * math.pi * k / seg),
                                    max(r, 0.004) * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for i in range(aneis):
        for k in range(seg):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Obj_Foguete_Chama")
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(_material_chama())
    ch = bpy.data.objects.new("Obj_Foguete_Chama", me)
    ch.parent = corpo_foguete                       # herda a inclinacao e a escala do foguete
    ch.location = (0.02, 0.0, -1.12)                # bocal (z local do corpo ~ -1.17)
    ch.visible_shadow = False
    ch.scale = (0, 0, 0)
    bpy.data.collections["Objetos_Autorais"].objects.link(ch)
    return ch


def _g(u, a):
    """Perfil de progresso 0..1: acelera (parabola) ate u=a e segue em velocidade constante."""
    v = 1.0 / (1.0 - a / 2.0)
    return v * u * u / (2 * a) if u < a else v * (a / 2 + (u - a))


def animar_foguete():
    emp = bpy.data.objects["Obj_Foguete"]
    corpo = bpy.data.objects["Obj_Foguete_Corpo"]
    chama = criar_chama(corpo)
    # menor (45%) mantendo a base no mesmo ponto do chao
    bpy.context.view_layer.update()
    cs = [corpo.matrix_world @ Vector(c) for c in corpo.bound_box]
    zmin = min(c.z for c in cs)
    p0 = emp.location.copy()
    p0.z = zmin + (p0.z - zmin) * FOGUETE_ESC
    emp.scale = (FOGUETE_ESC,) * 3
    fim = Vector((FOGUETE_FIM_XZ[0], p0.y, FOGUETE_FIM_XZ[1]))
    # chama acende em 250 (com flicker por modificador Noise) e fica ate o fim
    kf(chama, "scale", 1, (0, 0, 0), "CONSTANT")
    kf(chama, "scale", 250, (0, 0, 0), "CUBIC", "EASE_OUT")
    kf(chama, "scale", 262, (1.0, 1.0, 1.0), "LINEAR")
    kf(chama, "scale", 330, (1.0, 1.0, 1.0 + 0.6 * (CHAMA_ESC_FIM - 1)), "LINEAR")   # alonga com a velocidade
    kf(chama, "scale", F_FIM, (1.0, 1.0, CHAMA_ESC_FIM), "LINEAR")
    for fc in chama.animation_data.action.fcurves:
        if fc.data_path == "scale" and fc.array_index == 2:
            m = fc.modifiers.new("NOISE")
            m.scale, m.strength, m.phase = 3.0, 0.2, 1.7
            m.frame_start, m.use_restricted_range = 262, True
    # decolagem 270..360: ease-in ate 306 (parabola) e velocidade constante depois (sem parar no ar).
    # Amostrado a cada 6 frames com interpolacao linear (perfil exato, sem handles automaticos).
    a = (FOGUETE_FA - FOGUETE_F0) / (F_FIM - FOGUETE_F0)
    kf(emp, "location", 1, p0, "CONSTANT")
    kf(emp, "rotation_euler", 1, (0, 0, 0), "CONSTANT")
    for f in range(FOGUETE_F0, F_FIM + 1, 6):
        g = _g((f - FOGUETE_F0) / (F_FIM - FOGUETE_F0), a)
        kf(emp, "location", f, p0.lerp(fim, g), "LINEAR")
        kf(emp, "rotation_euler", f, (0, FOGUETE_INCLINA * g, 0), "LINEAR")
    log(f"foguete: p0={tuple(round(v, 2) for v in p0)} fim={tuple(round(v, 2) for v in fim)}")


# ------------------------------------------------------------------ iluminacao
def configurar_luz(motor):
    """Parte da AC04/AC05 (Sun + Area, fundo cinza, HDRI em raios glossy). No Eevee Next o HDRI
    entra tambem no World (Is Camera Ray -> cinza na camera; demais raios -> HDRI * HDRI_EEVEE)."""
    w = bpy.context.scene.world.node_tree
    N, L = w.nodes, w.links
    mix, lp = N["Mix Shader"], N["Light Path"]
    cinza, hdri = N["Background"], N["Background.001"]
    for i in range(3):
        for l in list(mix.inputs[i].links):
            L.remove(l)
    if motor == "CYCLES":                           # AC05 intacto: glossy -> HDRI, resto -> cinza
        hdri.inputs["Strength"].default_value = 1.0
        L.new(lp.outputs["Is Glossy Ray"], mix.inputs[0])
        L.new(cinza.outputs[0], mix.inputs[1])
        L.new(hdri.outputs[0], mix.inputs[2])
    else:                                           # Eevee: camera -> cinza; resto -> HDRI
        hdri.inputs["Strength"].default_value = HDRI_EEVEE
        L.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
        L.new(hdri.outputs[0], mix.inputs[1])
        L.new(cinza.outputs[0], mix.inputs[2])
    rim = bpy.data.objects.get("LUZ_Rim")
    if RIM and rim is None:
        d = bpy.data.lights.new("LUZ_Rim", "AREA")
        d.shape, d.size, d.size_y = "RECTANGLE", 7.0, 1.2
        d.color = (0.75, 0.85, 1.0)
        rim = bpy.data.objects.new("LUZ_Rim", d)
        bpy.data.collections["Luzes"].objects.link(rim)
        rim.location = (0.0, 1.8, 3.4)                       # atras e acima da palavra
        alvo = Vector((0.0, -0.3, 1.3))
        rim.rotation_euler = (alvo - rim.location).to_track_quat("-Z", "Y").to_euler()
    if rim is not None:
        rim.hide_render = not RIM
        rim.data.energy = RIM_ENERGIA


def configurar_motor(motor):
    s = bpy.context.scene
    configurar_luz(motor)
    s.render.use_motion_blur = MB_OBTURADOR > 0
    s.render.motion_blur_shutter = MB_OBTURADOR
    if motor == "CYCLES":
        s.render.engine = "CYCLES"
        s.cycles.samples, s.cycles.use_denoising, s.cycles.denoiser = CYCLES_SPP, True, "OPTIX"
        pref = bpy.context.preferences.addons["cycles"].preferences
        for tipo in ("OPTIX", "CUDA"):
            try:
                pref.compute_device_type = tipo
                pref.get_devices()
                if any(d.type == tipo for d in pref.devices):
                    for d in pref.devices:
                        d.use = d.type == tipo
                    s.cycles.device = "GPU"
                    break
            except Exception:
                continue
    else:
        s.render.engine = "BLENDER_EEVEE_NEXT"
        e = s.eevee
        e.taa_render_samples = 64
        e.use_raytracing = True                      # reflexos do robo espelhado
        e.ray_tracing_method = "SCREEN"
        e.ray_tracing_options.use_denoise = True
        e.ray_tracing_options.trace_max_roughness = 0.6
        e.use_shadows = True


# ------------------------------------------------------------------ renders
def _png(s, caminho, frame, w, h):
    s.frame_set(frame)
    r = s.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.image_settings.file_format = "PNG"
    r.filepath = caminho
    t0 = time.perf_counter()
    bpy.ops.render.render(write_still=True)
    return time.perf_counter() - t0


def render_previas(motor):
    s = bpy.context.scene
    os.makedirs(PREVIAS, exist_ok=True)
    configurar_motor(motor)
    for f in FRAMES_PREVIA:
        caminho = os.path.join(PREVIAS, f"previa_{f:03d}.png")
        dt = _png(s, caminho, f, 960, 540)
        log(f"previa {motor} f{f}: {dt:.1f}s -> {caminho}")


def render_teste_motor():
    """Frames 1/200/300/360 em 1920x1080: Eevee Next (World com HDRI + Is Camera Ray) e
    Cycles OptiX GPU 64 spp + denoise OptiX. Um frame de aquecimento (compilacao de shaders/
    kernels) fica fora da medida e e registrado a parte."""
    s = bpy.context.scene
    os.makedirs(TESTE_MOTOR, exist_ok=True)
    linhas = ["motor;frame;segundos"]
    for motor, rotulo in (("EEVEE", "eevee_next"), ("CYCLES", "cycles_optix_64spp")):
        configurar_motor(motor)
        aq = _png(s, os.path.join(TESTE_MOTOR, "_aquecimento.png"), 1, 1920, 1080)
        linhas.append(f"{rotulo};aquecimento(f1);{aq:.1f}")
        for f in FRAMES_MOTOR:
            dt = _png(s, os.path.join(TESTE_MOTOR, f"{rotulo}_f{f:03d}.png"), f, 1920, 1080)
            linhas.append(f"{rotulo};{f};{dt:.1f}")
            log(f"teste motor {rotulo} f{f}: {dt:.1f}s")
    os.remove(os.path.join(TESTE_MOTOR, "_aquecimento.png"))
    with open(os.path.join(TESTE_MOTOR, "tempos.csv"), "w", encoding="utf8") as fh:
        fh.write("\n".join(linhas) + "\n")


def render_texturas():
    """Recortes Cycles em tamanho real (1920x1080, render border com crop): foguete 270/315/360
    e computador 1/200/360."""
    s = bpy.context.scene
    os.makedirs(TEXTURAS, exist_ok=True)
    configurar_motor("CYCLES")
    O = bpy.data.objects
    alvos = (("foguete", ("Obj_Foguete_Corpo", "Obj_Foguete_Chama"), (270, 315, 360)),
             ("computador", ("Obj_Computador_Corpo",), (1, 200, 360)))
    for nome, objs, frames in alvos:
        for f in frames:
            s.frame_set(f)
            c = uniao([caixa_tela(O[o], s) for o in objs])
            pad = 0.02
            r = s.render
            r.use_border, r.use_crop_to_border = True, True
            r.border_min_x, r.border_max_x = max(0.0, c[0] - pad), min(1.0, c[2] + pad)
            r.border_min_y, r.border_max_y = max(0.0, c[1] - pad), min(1.0, c[3] + pad)
            dt = _png(s, os.path.join(TEXTURAS, f"{nome}_f{f:03d}.png"), f, 1920, 1080)
            log(f"textura {nome} f{f}: {dt:.1f}s")
    s.render.use_border = False


def render_final(motor):
    s = bpy.context.scene
    a, b = F_INI, F_FIM
    if os.environ.get("AP2_FRAMES"):
        a, b = (int(x) for x in os.environ["AP2_FRAMES"].split("-"))
    configurar_motor(motor)
    s.frame_start, s.frame_end = a, b
    s.render.resolution_x, s.render.resolution_y = 1920, 1080
    s.render.resolution_percentage = int(os.environ.get("AP2_ESCALA", "100"))
    s.render.image_settings.file_format = "FFMPEG"
    s.render.filepath = os.path.join(DESTINO, f"AP2_{AUTOR}")
    log(f"render final {motor} frames {a}-{b} -> {s.render.filepath}")
    bpy.ops.render.render(animation=True)
    # Blender acrescenta o intervalo ao nome; normaliza para AP2_<AUTOR>.mp4
    if (a, b) == (F_INI, F_FIM):
        cand = glob.glob(os.path.join(DESTINO, f"AP2_{AUTOR}*.mp4"))
        for c in cand:
            if os.path.abspath(c) != os.path.abspath(VIDEO):
                os.replace(c, VIDEO)


def _sequencia(pasta, w, h, spp, a, b, sobrescrever, motor="CYCLES"):
    """Render de animacao em sequencia PNG (Cycles); retorna segundos."""
    s = bpy.context.scene
    os.makedirs(pasta, exist_ok=True)
    configurar_motor(motor)
    s.cycles.samples = spp
    r = s.render
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGB"
    r.use_overwrite, r.use_placeholder = sobrescrever, not sobrescrever
    r.filepath = os.path.join(pasta, "f_")
    s.frame_start, s.frame_end = a, b
    t0 = time.perf_counter()
    bpy.ops.render.render(animation=True)
    dt = time.perf_counter() - t0
    log(f"sequencia {pasta} {a}-{b} {w}x{h} {spp}spp: {dt:.0f}s")
    return dt


def render_chama():
    s = bpy.context.scene
    d = os.path.join(SAIDA, "chama")
    os.makedirs(d, exist_ok=True)
    configurar_motor("CYCLES")
    for f in (260, 300, 360):
        dt = _png(s, os.path.join(d, f"chama_f{f}.png"), f, 1920, 1080)
        log(f"chama f{f}: {dt:.1f}s")


def verificar_composicao():
    ruins = blocos_sobre_palavra(range(190, 361, 5))
    bpy.context.scene.frame_set(360)
    O = bpy.data.objects
    c = uniao([caixa_tela(O["Obj_Foguete_Corpo"]), caixa_tela(O["Obj_Foguete_Chama"])])
    log("composicao: blocos sobre a Ibmec 190-360:", ruins or "nenhum")
    log("composicao: foguete+chama f360 =", tuple(round(v, 3) for v in c[:4]))
    log("composicao: palavra f360 =", tuple(round(v, 3) for v in caixa_palavra()[:4]))


# ------------------------------------------------------------------ main
def main():
    os.makedirs(DESTINO, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0   # sem .blend1
    bpy.ops.wm.open_mainfile(filepath=ORIGEM)             # AC05: somente leitura
    organizar_colecoes()
    configurar_cena()
    cab, bra = dividir_robo()
    animar_camera()
    animar_ibmec()
    animar_ponto_i()
    animar_blocos()
    animar_tela()
    animar_robo(cab, bra)
    animar_foguete()
    motor = os.environ.get("AP2_MOTOR", MOTOR_FINAL).upper()
    configurar_motor(motor)
    verificar_composicao()
    bpy.context.scene.frame_set(F_INI)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    log("salvo:", BLEND, "| motor:", motor)
    if os.environ.get("AP2_RENDER_TESTE") == "1":
        render_previas(motor)
    if os.environ.get("AP2_RENDER_MOTOR") == "1":
        render_teste_motor()
    if os.environ.get("AP2_RENDER_TEXTURAS") == "1":
        render_texturas()
    if os.environ.get("AP2_RENDER_CHAMA") == "1":
        render_chama()
    if os.environ.get("AP2_RENDER_RAPIDO") == "1":
        _sequencia(os.path.join(SAIDA, "teste_rapido"), 960, 540, 16, F_INI, F_FIM, True)
    if os.environ.get("AP2_RENDER_SEQ_FINAL") == "1":
        _sequencia(os.path.join(SAIDA, "frames"), 1920, 1080, CYCLES_SPP, F_INI, F_FIM, False)
    if os.environ.get("AP2_RENDER_FINAL") == "1":
        render_final(motor)


if __name__ == "__main__":
    main()
