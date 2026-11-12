"""
Validacao automatica da AC05. Abre AC5/AC05_<AUTOR>.blend e imprime uma tabela.

Executar:
    blender.exe --background --python AC5/validar_ac05.py
"""
import os
import sys

import bpy

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "AP1"))
import ap1_ibmec_conceito as ap1  # noqa: E402  (AUTOR e cores da marca)

BLEND = os.path.join(BASE, f"AC05_{ap1.AUTOR}.blend")
AUTORAIS = {"Obj_Robo_Corpo": "MAT_Espelho_PBR",
            "Obj_Computador_Corpo": "MAT_Madeira_PBR",
            "Obj_Foguete_Corpo": "MAT_Metal_Escovado_PBR"}
PALAVRA = {"Palavra_Ibmec": "MAT_Ibmec_PBR", "Palavra_Ponto_i": "MAT_Ibmec_Ponto_PBR"}
RESULT = []


def check(grupo, item, ok, detalhe=""):
    RESULT.append((grupo, item, bool(ok), detalhe))


def nos(mat, tipo):
    return [n for n in mat.node_tree.nodes if n.bl_idname == tipo]


def principled(mat):
    lista = nos(mat, "ShaderNodeBsdfPrincipled")
    return lista[0] if lista else None


def nos_arvore(nt, tipo):
    return [n for n in nt.nodes if n.bl_idname == tipo]


def origem(socket):
    return socket.links[0].from_node if socket.is_linked else None


def imagem_via(socket):
    """Segue o link ate achar um Image Texture (atravessa Map Range)."""
    n = origem(socket)
    while n is not None and n.bl_idname != "ShaderNodeTexImage":
        n = origem(n.inputs[0]) if n.bl_idname == "ShaderNodeMapRange" else None
    return n


def main():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    imgs_usadas = {}

    for nome, esperado in {**AUTORAIS, **PALAVRA}.items():
        mat = bpy.data.objects[nome].active_material
        check("Objeto", f"{nome}: material {esperado}",
              mat is not None and mat.name == esperado, mat.name if mat else "-")
        check("Objeto", f"{nome}: Principled BSDF",
              mat is not None and principled(mat) is not None)

    # --- valores PBR ---
    for esperado in AUTORAIS.values():
        mat = bpy.data.materials[esperado]
        b = principled(mat)
        met = b.inputs["Metallic"].default_value
        rug = b.inputs["Roughness"].default_value
        if esperado == "MAT_Madeira_PBR":
            check("PBR", f"{esperado}: Metallic = 0", met == 0.0, f"{met}")
        elif esperado == "MAT_Metal_Escovado_PBR":
            mr = nos(mat, "ShaderNodeMapRange")
            lo, hi = ((mr[0].inputs["To Min"].default_value,
                       mr[0].inputs["To Max"].default_value) if mr else (None, None))
            check("PBR", f"{esperado}: Metallic = 1", met == 1.0, f"{met}")
            check("PBR", f"{esperado}: Roughness 0.3..0.5 (Map Range, clamp)",
                  lo is not None and 0.3 <= lo and hi <= 0.5 and mr[0].clamp,
                  f"{lo:.2f}..{hi:.2f}")
        else:
            cb = b.inputs["Base Color"].default_value
            check("PBR", f"{esperado}: Metallic = 1", met == 1.0, f"{met}")
            check("PBR", f"{esperado}: Roughness 0..0.05", 0.0 <= rug <= 0.05, f"{rug}")
            check("PBR", f"{esperado}: Base Color clara", min(cb[:3]) >= 0.8,
                  f"{tuple(round(c, 2) for c in cb[:3])}")

    # --- mapas e colorspace ---
    for esperado in ("MAT_Madeira_PBR", "MAT_Metal_Escovado_PBR"):
        mat = bpy.data.materials[esperado]
        b = principled(mat)
        for canal in ("Base Color", "Roughness", "Normal"):
            sock = b.inputs[canal]
            if canal == "Normal":
                nm = origem(sock)
                ok_nm = nm is not None and nm.bl_idname == "ShaderNodeNormalMap"
                check("Mapas", f"{esperado}: Normal <- Normal Map", ok_nm)
                if ok_nm:
                    check("Mapas", f"{esperado}: Normal Map em Tangent Space",
                          nm.space == "TANGENT", nm.space)
                    t = origem(nm.inputs["Color"])
                    img = t.image if t is not None and t.bl_idname == "ShaderNodeTexImage" else None
                    check("Mapas", f"{esperado}: Normal Map <- Image Texture", img is not None)
                    if img:
                        imgs_usadas[img.name] = "dados"
                        check("Colorspace", f"{img.name} (normal)",
                              img.colorspace_settings.name == "Non-Color",
                              img.colorspace_settings.name)
            else:
                t = imagem_via(sock)
                check("Mapas", f"{esperado}: {canal} <- Image Texture", t is not None)
                if t:
                    dado = canal != "Base Color"
                    imgs_usadas[t.image.name] = "dados" if dado else "cor"
                    esp = "Non-Color" if dado else "sRGB"
                    check("Colorspace", f"{t.image.name} ({'dados' if dado else 'cor'})",
                          t.image.colorspace_settings.name == esp,
                          f"{t.image.colorspace_settings.name} (esperado {esp})")
        check("Mapas", f"{esperado}: Texture Coordinate (UV) + Mapping",
              bool(nos(mat, "ShaderNodeTexCoord")) and bool(nos(mat, "ShaderNodeMapping")))

    # --- UV ---
    for nome in ("Obj_Computador_Corpo", "Obj_Foguete_Corpo"):
        o = bpy.data.objects[nome]
        check("UV", f"{nome}: UV layer", len(o.data.uv_layers) >= 1,
              ", ".join(layer.name for layer in o.data.uv_layers))
        nm = nos(o.active_material, "ShaderNodeNormalMap")[0]
        check("UV", f"{nome}: Normal Map aponta para UV existente",
              nm.uv_map in o.data.uv_layers, nm.uv_map)

    # --- imagens empacotadas / sem caminho quebrado ---
    for img in bpy.data.images:
        if img.name in imgs_usadas:
            ok = img.packed_file is not None
            check("Imagens", f"{img.name}: empacotada", ok, f"{img.size[0]}x{img.size[1]}")
    check("Imagens", "6 imagens de textura em uso", len(imgs_usadas) == 6, f"{len(imgs_usadas)}")
    hdri = bpy.data.images.get("hdri_studio_small_08")
    check("Imagens", "HDRI hdri_studio_small_08 empacotado",
          hdri is not None and hdri.packed_file is not None)
    quebradas = [i.name for i in bpy.data.images
                 if i.source == "FILE" and i.packed_file is None
                 and not os.path.isfile(bpy.path.abspath(i.filepath))]
    check("Imagens", "nenhum caminho quebrado", not quebradas, ", ".join(quebradas))

    # --- Ibmec integra ---
    for nome, esperado in PALAVRA.items():
        mat = bpy.data.materials[esperado]
        b = principled(mat)
        sem_tex = not (nos(mat, "ShaderNodeTexImage") or nos(mat, "ShaderNodeNormalMap")
                       or nos(mat, "ShaderNodeBump"))
        livres = all(not b.inputs[k].is_linked
                     for k in ("Base Color", "Roughness", "Metallic", "Normal"))
        check("Ibmec", f"{nome}: sem textura/normal/bump", sem_tex and livres)
        rug = b.inputs["Roughness"].default_value
        check("Ibmec", f"{nome}: Metallic 0, Roughness moderada",
              b.inputs["Metallic"].default_value == 0 and 0.3 <= rug <= 0.7, f"rough={rug:.2f}")
    azul = principled(bpy.data.materials["MAT_Ibmec_PBR"]).inputs["Base Color"].default_value
    laranja = principled(bpy.data.materials["MAT_Ibmec_Ponto_PBR"]).inputs["Base Color"].default_value
    check("Ibmec", "azul da marca preservado",
          all(abs(a - b) < 1e-3 for a, b in zip(azul[:3], ap1.AZUL_IBMEC[:3])))
    check("Ibmec", "laranja do ponto preservado",
          all(abs(a - b) < 1e-3 for a, b in zip(laranja[:3], ap1.LARANJA_IBMEC[:3])))

    # --- cena ---
    s = bpy.context.scene
    check("Cena", "camera principal definida", s.camera is not None and s.camera.name == "Cam_Principal")
    check("Cena", "luzes da AC04 (Sol + Area)",
          {"LUZ_Principal", "LUZ_Preenchimento"} <= set(bpy.data.objects.keys()))
    # sem elementos auxiliares: as faixas Refletor_1..3 foram removidas (o HDRI resolveu)
    check("Cena", "faixas Refletor_* removidas (sem auxiliares)",
          not any(n.startswith("Refletor_") for n in bpy.data.objects.keys())
          and "AC05_Materiais_Texturas" not in bpy.data.collections)
    # World: cinza da AC04 + HDRI so para raios glossy
    w = s.world.node_tree
    saida = nos_arvore(w, "ShaderNodeOutputWorld")[0]
    mix = origem(saida.inputs["Surface"])
    ok_mix = mix is not None and mix.bl_idname == "ShaderNodeMixShader"
    lp = origem(mix.inputs["Fac"]) if ok_mix else None
    check("World", "Mix Shader com fator Light Path > Is Glossy Ray",
          lp is not None and lp.bl_idname == "ShaderNodeLightPath"
          and mix.inputs["Fac"].links[0].from_socket.name == "Is Glossy Ray")
    cinza = origem(mix.inputs[1]) if ok_mix else None
    cor = tuple(round(c, 3) for c in cinza.inputs["Color"].default_value[:3]) if cinza else None
    check("World", "entrada 0 (camera/difuso) = cinza da AC04 (0.32, 0.34, 0.40)",
          cinza is not None and cor == (0.32, 0.34, 0.4)
          and abs(cinza.inputs["Strength"].default_value - 1.0) < 1e-6, str(cor))
    hd = origem(mix.inputs[2]) if ok_mix else None
    env = origem(hd.inputs["Color"]) if hd else None
    check("World", "entrada 1 (glossy) = Environment Texture com HDRI",
          env is not None and env.bl_idname == "ShaderNodeTexEnvironment" and env.image is not None,
          env.image.name if env and env.image else "-")
    check("World", "HDRI empacotado", env is not None and env.image.packed_file is not None)
    # foguete: seams marcadas (UV por unwrap com seam atras)
    fog = bpy.data.objects["Obj_Foguete_Corpo"].data
    check("UV", "foguete: seams marcadas (arestas de emenda atras e aletas)",
          sum(1 for e in fog.edges if e.use_seam) > 0, f"{sum(1 for e in fog.edges if e.use_seam)} arestas")
    check("Cena", "motor de render salvo = Cycles", s.render.engine == "CYCLES", s.render.engine)

    # --- tabela (agrupada, mantendo a ordem de insercao) ---
    ordem = list(dict.fromkeys(r[0] for r in RESULT))
    RESULT.sort(key=lambda r: ordem.index(r[0]))
    larg = max(len(r[1]) for r in RESULT) + 2
    barra = "=" * (larg + 40)
    print("\n" + barra)
    print(f"VALIDACAO AC05  ({os.path.basename(BLEND)})")
    print(barra)
    grupo = None
    for g, item, ok, det in RESULT:
        if g != grupo:
            grupo = g
            print(f"\n[{g}]")
        print(f"  {'OK   ' if ok else 'FALHA'}  {item:<{larg}} {det}")
    falhas = [r for r in RESULT if not r[2]]
    print("\n" + "-" * (larg + 40))
    print(f"TOTAL: {len(RESULT) - len(falhas)}/{len(RESULT)} verificacoes OK")
    print(barra)


if __name__ == "__main__":
    main()
