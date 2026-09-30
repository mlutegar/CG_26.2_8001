"""Renderiza as imagens-capa da AP2 a partir do .blend aberto:
   cena_hd.png (Eevee 1080p), cena_capa_cycles.png (Cycles) e vertical (9:16).
Uso:  blender -b AP2/saida/AP2_MichelLutegar.blend --python AP2/_render_capas.py
"""
import os
import bpy

SAIDA = r"C:\Users\mlute\PycharmProjects\CG_26.2_8001\AP2\saida"
scn = bpy.context.scene
scn.render.resolution_x = 1920
scn.render.resolution_y = 1080
scn.render.image_settings.file_format = "PNG"

# 1) HD em Eevee
try:
    scn.eevee.taa_render_samples = 128
except AttributeError:
    pass
scn.render.filepath = os.path.join(SAIDA, "cena_hd.png")
bpy.ops.render.render(write_still=True)
print("HD_OK")

# 2) Capa em Cycles
scn.render.engine = "CYCLES"
try:
    scn.cycles.device = "GPU"
except Exception:
    pass
scn.cycles.samples = 150
scn.cycles.use_denoising = True
scn.render.filepath = os.path.join(SAIDA, "cena_capa_cycles.png")
bpy.ops.render.render(write_still=True)
print("CY_OK")

# 3) Versao vertical 9:16 (redes sociais) em Eevee
cam = bpy.data.objects.get("Cam_Principal")
if cam is not None:
    from mathutils import Vector as _V
    cam.location = cam.location + _V((-1.0, -3.0, 1.2))  # afasta p/ caber vertical
for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
    try:
        scn.render.engine = engine
        break
    except TypeError:
        continue
scn.render.resolution_x = 1080
scn.render.resolution_y = 1920
scn.render.filepath = os.path.join(SAIDA, "cena_capa_vertical.png")
bpy.ops.render.render(write_still=True)
print("VERT_OK")
