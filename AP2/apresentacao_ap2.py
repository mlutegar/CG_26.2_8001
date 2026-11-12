"""AP2: modo apresentacao no Blender 4.5.

Uso (a partir da raiz do repositorio):
    blender.exe AP2/AP2_MichelLutegar.blend --python AP2/apresentacao_ap2.py

O script NUNCA salva o .blend. Tudo o que ele muda (workspaces, selecao, amostras do Cycles)
vale so para esta sessao. O autosave e desligado e as preferencias nao sao gravadas.

Variaveis de ambiente (so para teste):
    AP2_FORCAR_CPU=1       simula um PC sem GPU
    AP2_CAPTURAS=<pasta>   salva um PNG de cada workspace e fecha o Blender
"""
import os

import bpy

AMOSTRAS_CPU = 16
PASSO = 0.5          # segundos entre etapas (a interface precisa redesenhar entre elas)
ESPERA_MAX = 60      # segundos esperando a interface carregar

OBJ_COMPUTADOR = "Obj_Computador_Corpo"
MAT_MADEIRA = "MAT_Madeira_PBR"
IMG_MADEIRA = "madeira_basecolor"
OBJ_ANIM = ("Palavra_Ibmec", "Cam_Principal")


def aviso(msg):
    print("[AP2] " + msg, flush=True)


# ---------------------------------------------------------------- preferencias e Cycles
def proteger_sessao():
    """Sem autosave e sem gravar preferencias."""
    p = bpy.context.preferences
    p.filepaths.use_auto_save_temporary_files = False
    try:
        p.use_preferences_save = False
    except Exception:
        pass


def detectar_gpu():
    """Devolve (tipo, nome) da GPU OptiX/CUDA, ou None."""
    if os.environ.get("AP2_FORCAR_CPU") == "1":
        return None
    try:
        pref = bpy.context.preferences.addons["cycles"].preferences
    except KeyError:
        return None
    for tipo in ("OPTIX", "CUDA"):
        try:
            pref.compute_device_type = tipo
            pref.refresh_devices()
            gpus = [d for d in pref.devices if d.type == tipo]
        except Exception:
            continue
        if gpus:
            for d in pref.devices:
                d.use = d.type == tipo
            return tipo, ", ".join(d.name for d in gpus)
    return None


def configurar_cycles():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    gpu = detectar_gpu()
    if gpu:
        s.cycles.device = "GPU"
        aviso("Dispositivo Cycles: GPU %s (%s). Amostras do F12 mantidas: %d."
              % (gpu[0], gpu[1], s.cycles.samples))
    else:
        try:
            bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "NONE"
        except Exception:
            pass
        s.cycles.device = "CPU"
        s.cycles.samples = AMOSTRAS_CPU
        s.cycles.use_denoising = True
        s.cycles.denoiser = "OPENIMAGEDENOISE"
        aviso("AVISO: nenhuma GPU OptiX/CUDA encontrada. Dispositivo Cycles: CPU. "
              "F12 reduzido para %d amostras com denoise (so nesta sessao)." % AMOSTRAS_CPU)


# ---------------------------------------------------------------- utilitarios de interface
def janela():
    return bpy.context.window_manager.windows[0]


def areas(tipo):
    return [a for a in janela().screen.areas if a.type == tipo]


def maior(lista):
    return max(lista, key=lambda a: a.width * a.height) if lista else None


def regiao(area, tipo="WINDOW"):
    for r in area.regions:
        if r.type == tipo:
            return r
    return None


def ctx(area):
    """Contexto de override para operadores de uma area."""
    return bpy.context.temp_override(window=janela(), screen=janela().screen, area=area,
                                     region=regiao(area))


def espaco(area):
    return area.spaces.active


def dividir(area, direcao, fator):
    """Divide a area e devolve a nova area (a que nao existia antes)."""
    antes = {a.as_pointer() for a in janela().screen.areas}
    with ctx(area):
        bpy.ops.screen.area_split(direction=direcao, factor=fator)
    novas = [a for a in janela().screen.areas if a.as_pointer() not in antes]
    return novas[0] if novas else None


def garantir(tipo, ui_type=None, base_tipo="VIEW_3D", direcao="VERTICAL", fator=0.5):
    """Devolve uma area do tipo pedido; se nao existir, divide a area base (maior) e converte."""
    ja = areas(tipo)
    if ja:
        return maior(ja)
    base = maior(areas(base_tipo))
    nova = dividir(base, direcao, fator)
    nova.type = tipo
    if ui_type:
        nova.ui_type = ui_type
    return nova


def trocar_tamanho(grande, pequena):
    """Troca o conteudo de duas areas para que `grande` (hoje a menor) ocupe o espaco maior."""
    tg, tp = grande.ui_type, pequena.ui_type
    grande.ui_type, pequena.ui_type = tp, tg


def ampliar_ate_caber(area, arvore, margem=0.05):
    """node.view_all deixa folga demais: aproxima a vista enquanto todos os nos couberem na regiao."""
    r = regiao(area)
    v2d = r.view2d

    def cabe():
        for n in arvore.nodes:
            x0, y1 = n.location
            x1, y0 = x0 + n.dimensions.x, y1 - n.dimensions.y
            ax, ay = v2d.view_to_region(x0, y0, clip=False)
            bx, by = v2d.view_to_region(x1, y1, clip=False)
            if ax < r.width * margem or bx > r.width * (1 - margem)                     or ay < r.height * margem or by > r.height * (1 - margem):
                return False
        return True

    with ctx(area):
        for _ in range(12):
            bpy.ops.view2d.zoom_in()
            if not cabe():
                bpy.ops.view2d.zoom_out()
                break


def afastar_mouse(area):
    """Tira o ponteiro de cima dos botoes (evita tooltip na captura e na apresentacao)."""
    r = regiao(area)
    janela().cursor_warp(r.x + r.width // 2, r.y + r.height // 2)


def selecionar(nomes, ativo):
    """Seleciona so os objetos pedidos e define o ativo (modo objeto)."""
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for n in nomes:
        o = bpy.data.objects.get(n)
        if o is not None:
            o.select_set(True)
    vl.objects.active = bpy.data.objects[ativo]


def para_modo_objeto():
    vl = bpy.context.view_layer
    ob = vl.objects.active
    if ob is not None and ob.mode != "OBJECT":
        v3 = maior(areas("VIEW_3D"))
        if v3 is not None:
            with ctx(v3):
                bpy.ops.object.mode_set(mode="OBJECT")
        else:
            bpy.ops.object.mode_set(mode="OBJECT")


def overlays_minimos(sp):
    ov = sp.overlay
    ov.show_overlays = True
    for nome in ("show_floor", "show_axis_x", "show_axis_y", "show_axis_z", "show_cursor",
                 "show_extras", "show_relationship_lines", "show_text", "show_stats",
                 "show_outline_selected", "show_object_origins", "show_bones",
                 "show_motion_paths", "show_annotation"):
        if hasattr(ov, nome):
            setattr(ov, nome, False)


# ---------------------------------------------------------------- preparo de cada workspace
# Cada preparo e um gerador: cada "yield" devolve o controle ao Blender para ele redesenhar.
def preparar_animation():
    para_modo_objeto()
    bpy.context.scene.frame_set(1)
    selecionar(OBJ_ANIM, "Palavra_Ibmec")
    yield
    v3s = sorted(areas("VIEW_3D"), key=lambda a: a.x)
    if areas("GRAPH_EDITOR"):
        graf = maior(areas("GRAPH_EDITOR"))
    elif len(v3s) >= 2:
        # a vista 3D pequena da esquerda vira o Graph Editor; a maior fica com a camera
        graf = v3s[0]
        graf.ui_type = "FCURVES"
    else:
        graf = garantir("GRAPH_EDITOR", "FCURVES", "VIEW_3D", "VERTICAL", 0.45)
    yield
    for v3 in areas("VIEW_3D"):
        sp = espaco(v3)
        sp.region_3d.view_perspective = "CAMERA"
        sp.shading.type = "MATERIAL"
        sp.show_gizmo = False
        overlays_minimos(sp)
        sp.show_region_toolbar = False
        sp.show_region_ui = False
    for tl in areas("DOPESHEET_EDITOR"):
        tl.ui_type = "TIMELINE"
        s = espaco(tl)
        s.show_markers = True
        s.show_region_ui = False
    gs = espaco(graf)
    gs.dopesheet.show_only_selected = True
    gs.show_region_ui = False
    yield
    with ctx(graf):
        bpy.ops.graph.view_all()
    for v3 in areas("VIEW_3D"):
        with ctx(v3):
            bpy.ops.view3d.view_center_camera()    # enquadra a camera no viewport
    bpy.context.scene.frame_set(1)
    yield


def preparar_shading():
    para_modo_objeto()
    selecionar((OBJ_COMPUTADOR,), OBJ_COMPUTADOR)
    mat = bpy.data.materials[MAT_MADEIRA]
    corpo = bpy.data.objects[OBJ_COMPUTADOR]
    for i, sl in enumerate(corpo.material_slots):
        if sl.material == mat:
            corpo.active_material_index = i
    nodes = garantir("NODE_EDITOR", "ShaderNodeTree", "VIEW_3D", "HORIZONTAL", 0.35)
    v3 = maior(areas("VIEW_3D"))
    if v3 is not None and v3.width * v3.height > nodes.width * nodes.height:
        trocar_tamanho(nodes, v3)   # o Shader Editor passa a ocupar a area grande
    yield
    nodes = maior(areas("NODE_EDITOR"))
    if not janela().screen.show_fullscreen:
        with ctx(nodes):
            bpy.ops.screen.screen_full_area(use_hide_panels=False)   # Shader Editor em tela cheia (Ctrl+Espaco volta)
        yield
        nodes = maior(areas("NODE_EDITOR"))
    sp = espaco(nodes)
    sp.shader_type = "OBJECT"
    sp.tree_type = "ShaderNodeTree"
    sp.pin = False
    sp.show_region_toolbar = False
    sp.show_region_ui = False
    for a in areas("VIEW_3D"):
        espaco(a).shading.type = "MATERIAL"
    yield
    # node.view_all so afasta a vista (nunca aproxima): volta a 1:1 e deixa ele afastar ate caber
    with ctx(nodes):
        bpy.ops.view2d.reset()
    yield
    for _ in range(2):          # 2 passadas: a regiao so tem o tamanho final depois de redesenhar
        with ctx(nodes):
            bpy.ops.node.view_all()
        yield
    ampliar_ate_caber(nodes, bpy.data.materials[MAT_MADEIRA].node_tree)
    yield


def preparar_uv():
    para_modo_objeto()
    selecionar((OBJ_COMPUTADOR,), OBJ_COMPUTADOR)
    v3 = maior(areas("VIEW_3D"))
    with ctx(v3):
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.mesh.select_all(action="SELECT")
    imgs = areas("IMAGE_EDITOR")
    if not imgs:
        garantir("IMAGE_EDITOR", None, "VIEW_3D", "VERTICAL", 0.5)
    yield
    img = maior(areas("IMAGE_EDITOR"))
    sp = espaco(img)
    sp.mode = "UV"
    sp.image = bpy.data.images[IMG_MADEIRA]
    try:
        sp.uv_editor.show_uv = True
    except Exception:
        pass
    for a in areas("IMAGE_EDITOR"):
        espaco(a).uv_editor.show_stretch = False
    yield
    with ctx(img):
        try:
            bpy.ops.uv.select_all(action="SELECT")
        except Exception as e:
            aviso("uv.select_all falhou: %s" % e)
        bpy.ops.image.view_selected()
    yield


PREPAROS = {
    "Animation": preparar_animation,
    "Shading": preparar_shading,
    "UV Editing": preparar_uv,
}
ORDEM_INICIAL = ["Shading", "UV Editing", "Animation"]  # termina em Animation


class Apresentacao:
    def __init__(self):
        self.fila = list(ORDEM_INICIAL)
        self.gerador = None
        self.atual = None          # workspace cujo preparo esta em andamento
        self.preparado = None      # ultimo workspace preparado (para detectar troca manual)
        self.capturas = os.environ.get("AP2_CAPTURAS")
        self.espera = 0
        self.pendente = None

    def pronto(self):
        wm = bpy.context.window_manager
        if not wm.windows:
            return False
        w = wm.windows[0]
        if w.screen is None or w.workspace is None:
            return False
        ars = list(w.screen.areas)
        return bool(ars) and all(a.width > 50 and regiao(a) is not None and regiao(a).width > 0 for a in ars)

    def afastar(self, nome):
        principal = {"Animation": "VIEW_3D", "Shading": "NODE_EDITOR", "UV Editing": "IMAGE_EDITOR"}.get(nome)
        if principal and areas(principal):
            afastar_mouse(maior(areas(principal)))

    def estado(self, nome):
        """Resumo do que esta na tela (so no modo de teste)."""
        import bmesh
        vl = bpy.context.view_layer
        ob = vl.objects.active
        info = {"workspace": janela().workspace.name, "frame": bpy.context.scene.frame_current,
                "ativo": ob.name if ob else None, "modo": ob.mode if ob else None,
                "selecionados": sorted(o.name for o in vl.objects if o.select_get())}
        if nome == "Animation":
            v3 = maior(areas("VIEW_3D"))
            info["vista"] = espaco(v3).region_3d.view_perspective
            info["shading"] = espaco(v3).shading.type
            info["graph_editor"] = bool(areas("GRAPH_EDITOR"))
            info["timeline_marcadores"] = [espaco(a).show_markers for a in areas("DOPESHEET_EDITOR")]
        elif nome == "Shading":
            n = maior(areas("NODE_EDITOR"))
            info["node_tree"] = espaco(n).edit_tree.name if espaco(n).edit_tree else None
            info["tela_cheia"] = janela().screen.show_fullscreen
        elif nome == "UV Editing":
            bm = bmesh.from_edit_mesh(ob.data)
            info["faces_sel/total"] = "%d/%d" % (sum(f.select for f in bm.faces), len(bm.faces))
            info["imagem"] = espaco(maior(areas("IMAGE_EDITOR"))).image.name
        aviso("estado " + nome + ": " + repr(info))

    def capturar(self, nome):
        if not self.capturas:
            return
        self.estado(nome)
        os.makedirs(self.capturas, exist_ok=True)
        arq = os.path.join(self.capturas, nome.replace(" ", "_").lower() + ".png")
        bpy.ops.screen.screenshot(filepath=arq)
        aviso("captura: " + arq)

    def tick(self):
        try:
            return self._tick()
        except Exception as e:
            import traceback
            traceback.print_exc()
            aviso("erro no modo apresentacao: %s" % e)
            return None

    def _tick(self):
        if not self.pronto():
            self.espera += PASSO
            if self.espera > ESPERA_MAX:
                aviso("interface nao carregou, modo apresentacao cancelado.")
                return None
            return PASSO
        w = janela()

        # 1) etapa em andamento
        if self.gerador is not None:
            try:
                next(self.gerador)
                return PASSO
            except StopIteration:
                self.gerador = None
                self.preparado = self.atual
                self.atual = None
                self.afastar(self.preparado)
                self.pendente = self.preparado   # o screenshot sai no proximo ciclo, ja redesenhado
                return PASSO

        if self.pendente:
            self.capturar(self.pendente)
            self.pendente = None
            if not self.fila:
                if self.capturas:
                    bpy.ops.wm.quit_blender()
                    return None
                aviso("modo apresentacao pronto (workspace: %s)." % self.preparado)
            return PASSO

        # 2) proximo workspace da fila inicial
        if self.fila:
            alvo = self.fila[0]
            if w.workspace.name != alvo:
                w.workspace = bpy.data.workspaces[alvo]
                return PASSO          # espera a interface trocar de tela
            self.fila.pop(0)
            self.atual = alvo
            self.gerador = PREPAROS[alvo]()
            return PASSO

        # 3) depois de pronto: se o usuario trocar de workspace, prepara de novo
        nome = w.workspace.name
        if nome != self.preparado and nome in PREPAROS:
            self.atual = nome
            self.gerador = PREPAROS[nome]()
        elif nome != self.preparado:
            para_modo_objeto()
            self.preparado = nome
        return PASSO


def principal():
    proteger_sessao()
    configurar_cycles()
    if bpy.app.background:
        aviso("modo background: apenas configuracao do Cycles aplicada.")
        return
    app = Apresentacao()
    bpy.app.timers.register(app.tick, first_interval=1.0, persistent=False)


principal()
