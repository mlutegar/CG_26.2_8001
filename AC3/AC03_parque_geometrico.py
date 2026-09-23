import bpy
import bmesh
import math

ALUNO = "MichelLutegar"
COLECAO = "AC03_transformacoes"
FRAME_INICIAL = 1
FRAME_MEIO = 60
FRAME_FINAL = 120
FPS = 24


def limpar_colecao(nome):
    if nome in bpy.data.collections:
        col = bpy.data.collections[nome]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
    nova = bpy.data.collections.new(nome)
    bpy.context.scene.collection.children.link(nova)
    return nova


def mover_para_colecao(obj, colecao):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    colecao.objects.link(obj)


colecao = limpar_colecao(COLECAO)

bpy.ops.mesh.primitive_plane_add(size=1.6, location=(-3, -2, 0))
quadrado = bpy.context.active_object
quadrado.name = "obj2d_quadrado"
mover_para_colecao(quadrado, colecao)

bpy.ops.mesh.primitive_plane_add(size=1.6, location=(0, -2, 0))
triangulo = bpy.context.active_object
triangulo.name = "obj2d_triangulo"
mover_para_colecao(triangulo, colecao)
malha = triangulo.data
bm = bmesh.new()
bm.verts.new((-1.0, -1.0, 0.0))
bm.verts.new((1.0, -1.0, 0.0))
bm.verts.new((0.0, 1.0, 0.0))
bm.verts.ensure_lookup_table()
bm.faces.new(bm.verts)
bm.to_mesh(malha)
bm.free()

bpy.ops.mesh.primitive_circle_add(radius=0.8, vertices=32,
                                  fill_type='NGON', location=(3, -2, 0))
circulo = bpy.context.active_object
circulo.name = "obj2d_circulo"
mover_para_colecao(circulo, colecao)
circulo.scale = (1.3, 0.7, 1.0)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-3, 1.5, 0.8))
cubo = bpy.context.active_object
cubo.name = "obj3d_cubo"
mover_para_colecao(cubo, colecao)
cubo.rotation_euler = (math.radians(25), math.radians(15), math.radians(40))
cubo.scale = (1.0, 0.7, 1.2)

bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=1.6, location=(0, 1.5, 0.8))
cilindro = bpy.context.active_object
cilindro.name = "obj3d_cilindro"
mover_para_colecao(cilindro, colecao)
cilindro.rotation_euler = (math.radians(90), 0, 0)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(3, 1.5, 0.8))
esfera = bpy.context.active_object
esfera.name = "obj3d_esfera"
mover_para_colecao(esfera, colecao)

circulo.parent = quadrado
circulo.matrix_parent_inverse = quadrado.matrix_world.inverted()

cena = bpy.context.scene
cena.render.fps = FPS
cena.frame_start = FRAME_INICIAL
cena.frame_end = FRAME_FINAL


def key(obj, frame, location=None, rotation_euler=None, scale=None):
    cena.frame_set(frame)
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation_euler is not None:
        obj.rotation_euler = rotation_euler
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)


key(quadrado, FRAME_INICIAL, location=(-3, -2, 0), rotation_euler=(0, 0, 0))
key(quadrado, FRAME_MEIO, location=(-1.5, -2, 0),
    rotation_euler=(0, 0, math.radians(90)))
key(quadrado, FRAME_FINAL, location=(0, -2.2, 0),
    rotation_euler=(0, 0, math.radians(180)))

key(esfera, FRAME_INICIAL, scale=(1, 1, 1), rotation_euler=(0, 0, 0))
key(esfera, FRAME_FINAL, scale=(1.8, 1.8, 0.5),
    rotation_euler=(math.radians(120), 0, math.radians(200)))

def aplicar_easing(obj):
    if not (obj.animation_data and obj.animation_data.action):
        return
    action = obj.animation_data.action
    if hasattr(action, "fcurves"):          # Blender <= 4.3
        curvas = action.fcurves
    else:                                    # Blender 4.4+ (slotted actions)
        curvas = [fc for layer in action.layers
                  for strip in layer.strips
                  for cbag in strip.channelbags
                  for fc in cbag.fcurves]
    for fcurve in curvas:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.easing = 'EASE_IN_OUT'


aplicar_easing(esfera)

cena.frame_set(FRAME_INICIAL)

bpy.ops.object.camera_add(location=(0, -11, 7),
                          rotation=(math.radians(58), 0, 0))
camera = bpy.context.active_object
camera.name = "AC03_camera"
camera.data.lens = 28
mover_para_colecao(camera, colecao)
cena.camera = camera

bpy.ops.object.light_add(type='SUN', location=(4, -4, 10))
luz = bpy.context.active_object
luz.name = "AC03_sol"
mover_para_colecao(luz, colecao)
luz.data.energy = 3.0

cena.render.image_settings.file_format = 'PNG'
cena.render.filepath = "//AC03_%s.png" % ALUNO

bpy.ops.render.render(write_still=True)
