"""
Capturas da AC05 com a interface do Blender aberta (nao funciona em --background).

Executar a partir da raiz do repositorio:
    blender.exe AC5/AC05_MichelLutegar.blend --python AC5/capturas_ac05.py

O .blend NAO e salvo: o script captura e fecha com wm.quit_blender.
Alterações feitas na sessao (workspace, modo, shading) ficam so na memoria.
"""
import os
import traceback

import bpy

BASE = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(BASE, "saida")
os.makedirs(SAIDA, exist_ok=True)

AMOSTRAS_RENDERED = 128   # amostras do viewport Cycles
ESPERA_RENDERED = 75.0    # segundos para o ruido limpar (CPU)
ZOOM_PASSOS = 9
LOG = []


def log(msg):
    print("[capturas]", msg, flush=True)
    LOG.append(msg)


def janela():
    return bpy.context.window_manager.windows[0]


def area_de(tipo, ui=None):
    for a in janela().screen.areas:
        if a.type == tipo and (ui is None or a.ui_type == ui):
            return a
    return None


def regiao_window(area):
    return next(r for r in area.regions if r.type == "WINDOW")


def override(area):
    return bpy.context.temp_override(window=janela(), screen=janela().screen,
                                     area=area, region=regiao_window(area))


def ir_workspace(nome):
    janela().workspace = bpy.data.workspaces[nome]


def maximizar_area(area):
    """Ocupa a janela inteira com a area (equivale a Ctrl+Espaco)."""
    with override(area):
        bpy.ops.screen.screen_full_area(use_hide_panels=True)


def restaurar_area():
    a = janela().screen.areas[0]
    with override(a):
        bpy.ops.screen.back_to_previous()


def redesenhar(area):
    """Forca um redraw da janela (a area recem-maximizada pode estar desatualizada)."""
    with override(area):
        bpy.ops.wm.redraw_timer(type="DRAW_WIN_SWAP", iterations=2)


def shot(area, nome):
    janela().cursor_warp(janela().width - 3, janela().height - 3)  # sem tooltip
    redesenhar(area)
    r = regiao_window(area)
    log(f"area {nome}: {area.width}x{area.height} regiao {r.width}x{r.height}")
    caminho = os.path.join(SAIDA, nome)
    with override(area):
        bpy.ops.screen.screenshot_area(filepath=caminho)
    log(f"salvo {nome}")


def selecionar_unico(obj):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


# ---------------------------------------------------------------- etapas
# Cada etapa devolve o atraso (s) ate a proxima; o timer reentra na proxima.

def etapa_inicio():
    log("interface pronta")
    bpy.context.scene.render.engine = "CYCLES"   # so na memoria
    return 1.0


def etapa_shader_1():
    ir_workspace("Shading")
    return 2.0


def etapa_shader_2():
    obj = bpy.data.objects["Obj_Computador_Corpo"]
    selecionar_unico(obj)
    obj.active_material_index = obj.data.materials.find("MAT_Madeira_PBR")
    ne = area_de("NODE_EDITOR")
    sp = ne.spaces.active
    sp.shader_type = "OBJECT"
    sp.pin = False
    maximizar_area(ne)
    return 2.0


def etapa_shader_3():
    ne = area_de("NODE_EDITOR")
    sp = ne.spaces.active
    sp.overlay.show_context_path = True
    mat = bpy.data.materials["MAT_Madeira_PBR"]
    # deixa so a arvore do material ativo; seleciona todos os nos p/ enquadrar
    with override(ne):
        bpy.ops.node.select_all(action="DESELECT")
        bpy.ops.node.view_all()
    log(f"node editor mostra: {sp.edit_tree.name if sp.edit_tree else None}; "
        f"nos={len(mat.node_tree.nodes)}")
    return 1.5


def etapa_shader_4():
    ne = area_de("NODE_EDITOR")
    redesenhar(ne)
    with override(ne):
        bpy.ops.node.select_all(action="SELECT")
        bpy.ops.node.view_selected()   # enquadra mais justo que view_all
        bpy.ops.node.select_all(action="DESELECT")
    for _ in range(ZOOM_PASSOS):   # o view_all deixa muita margem; aproxima mais
        with override(ne):
            bpy.ops.view2d.zoom_in()
    redesenhar(ne)
    return 1.5


def etapa_shader_5():
    shot(area_de("NODE_EDITOR"), "AC05_shader_editor.png")
    restaurar_area()
    return 1.0


def etapa_uv_1():
    ir_workspace("UV Editing")
    return 2.0


def etapa_uv_2():
    obj = bpy.data.objects["Obj_Computador_Corpo"]
    selecionar_unico(obj)
    if bpy.context.object.mode != "EDIT":
        with override(area_de("VIEW_3D")):
            bpy.ops.object.mode_set(mode="EDIT")
    return 1.5


def etapa_uv_3():
    v3d = area_de("VIEW_3D")
    with override(v3d):
        bpy.ops.mesh.select_mode(type="FACE")
        bpy.ops.mesh.select_all(action="SELECT")
    ie = area_de("IMAGE_EDITOR")
    sp = ie.spaces.active
    ie.ui_type = "UV"
    sp = ie.spaces.active
    sp.image = bpy.data.images["madeira_basecolor"]
    sp.uv_editor.show_stretch = False
    with override(ie):
        bpy.ops.uv.select_all(action="SELECT")
    log(f"modo={bpy.context.object.mode}, uv_layer="
        f"{bpy.context.object.data.uv_layers.active.name}")
    return 1.5


def etapa_uv_4():
    ie = area_de("IMAGE_EDITOR")
    maximizar_area(ie)
    return 2.0


def etapa_uv_5():
    ie = area_de("IMAGE_EDITOR")
    redesenhar(ie)
    with override(ie):
        bpy.ops.image.view_all(fit_view=True)
    return 1.5


def etapa_uv_6():
    shot(area_de("IMAGE_EDITOR"), "AC05_uv_editor.png")
    # bonus: layout UV (so exporta o que esta selecionado, e uma imagem 2D)
    ie = area_de("IMAGE_EDITOR")
    try:
        with override(ie):
            bpy.ops.uv.export_layout(filepath=os.path.join(SAIDA, "AC05_uv_layout.png"),
                                     export_all=True, mode="PNG", size=(2048, 2048),
                                     opacity=0.8)
        log("salvo AC05_uv_layout.png")
    except Exception as e:  # noqa: BLE001
        log(f"uv_layout falhou: {e}")
    restaurar_area()
    return 1.0


def etapa_vp_1():
    # sai do modo edicao antes de ir ao viewport da camera
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        with override(area_de("VIEW_3D")):
            bpy.ops.object.mode_set(mode="OBJECT")
    ir_workspace("Layout")
    return 2.0


def etapa_vp_2():
    v3d = area_de("VIEW_3D")
    sp = v3d.spaces.active
    sp.overlay.show_overlays = False
    sp.show_gizmo = False
    sp.shading.type = "MATERIAL"
    sp.region_3d.view_perspective = "CAMERA"
    maximizar_area(v3d)
    return 2.0


def etapa_vp_3():
    v3d = area_de("VIEW_3D")
    with override(v3d):
        bpy.ops.view3d.view_camera()
        # garante camera ativa e enquadrada
    sp = v3d.spaces.active
    sp.region_3d.view_perspective = "CAMERA"
    with override(v3d):
        bpy.ops.view3d.view_center_camera()
    for o in bpy.context.view_layer.objects:
        o.select_set(False)   # sem contorno de selecao
    return 6.0   # Eevee compila shaders


def etapa_vp_4():
    shot(area_de("VIEW_3D"), "AC05_viewport_material_preview.png")
    bpy.context.scene.cycles.preview_samples = AMOSTRAS_RENDERED
    bpy.context.scene.cycles.use_preview_denoising = True
    bpy.context.scene.cycles.device = "CPU"
    area_de("VIEW_3D").spaces.active.shading.type = "RENDERED"
    log(f"Rendered Cycles, espera {ESPERA_RENDERED:.0f}s")
    return ESPERA_RENDERED


def etapa_vp_5():
    shot(area_de("VIEW_3D"), "AC05_viewport_rendered.png")
    return 1.0


def etapa_fim():
    log("fim; fechando sem salvar")
    bpy.ops.wm.quit_blender()
    return None


ETAPAS = [etapa_inicio, etapa_shader_1, etapa_shader_2, etapa_shader_3, etapa_shader_4,
          etapa_shader_5, etapa_uv_1, etapa_uv_2, etapa_uv_3, etapa_uv_4, etapa_uv_5,
          etapa_uv_6, etapa_vp_1, etapa_vp_2, etapa_vp_3, etapa_vp_4, etapa_vp_5, etapa_fim]
_i = [0]
_espera_ui = [0]


def tick():
    # espera a janela/UI existir (a interface carrega depois do script)
    if not bpy.context.window_manager.windows:
        return 0.5
    if _i[0] == 0 and _espera_ui[0] < 6:
        _espera_ui[0] += 1
        return 0.5
    if _i[0] >= len(ETAPAS):
        return None
    etapa = ETAPAS[_i[0]]
    _i[0] += 1
    try:
        return etapa()
    except Exception:  # noqa: BLE001
        log(f"ERRO em {etapa.__name__}:\n{traceback.format_exc()}")
        # segue para a proxima etapa; o fim sempre fecha o Blender
        return 0.5 if _i[0] < len(ETAPAS) else None


bpy.app.timers.register(tick, first_interval=2.0)
