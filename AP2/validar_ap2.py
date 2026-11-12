"""
Validacao automatica da AP2. Abre AP2/AP2_<AUTOR>.blend e imprime uma tabela.

Executar:
    blender.exe --background --python AP2/validar_ap2.py
(AP2_DESTINO opcional, como no script principal)
"""
import os
import sys

import bpy

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "..", "AP1"))
sys.path.insert(0, BASE)
import ap1_ibmec_conceito as ap1  # noqa: E402
import ap2_ibmec_final as ap2  # noqa: E402  (helpers de projecao na camera)

DESTINO = os.path.abspath(os.environ.get("AP2_DESTINO", BASE))
BLEND = os.path.join(DESTINO, f"AP2_{ap1.AUTOR}.blend")
AUTORAIS = {"Obj_Robo_Corpo": "MAT_Espelho_PBR",
            "Obj_Computador_Corpo": "MAT_Madeira_PBR",
            "Obj_Foguete_Corpo": "MAT_Metal_Escovado_PBR"}
PALAVRA = {"Palavra_Ibmec": "MAT_Ibmec_PBR", "Palavra_Ponto_i": "MAT_Ibmec_Ponto_PBR"}
COLECOES = ("Marca", "Objetos_Autorais", "Cenario", "Cameras", "Luzes")
MARCADORES = {1: "Inicio", 73: "Desenvolvimento", 241: "Encerramento"}
RESULT = []


def check(grupo, item, ok, detalhe=""):
    RESULT.append((grupo, item, bool(ok), detalhe))


def fcurves(idb):
    ad = getattr(idb, "animation_data", None)
    return list(ad.action.fcurves) if ad and ad.action else []


def faixa_keys(idb):
    ks = [p.co[0] for fc in fcurves(idb) for p in fc.keyframe_points]
    return (min(ks), max(ks)) if ks else None


def varia(idb):
    """True se algum F-Curve tem valores diferentes entre seus keyframes."""
    for fc in fcurves(idb):
        v = [p.co[1] for p in fc.keyframe_points]
        if v and max(v) - min(v) > 1e-6:
            return True
    return False


def main():
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    s = bpy.context.scene
    O = bpy.data.objects

    # --- tempo ---
    check("Tempo", "frames 1 a 360", (s.frame_start, s.frame_end) == (1, 360),
          f"{s.frame_start}-{s.frame_end}")
    check("Tempo", "24 fps", s.render.fps == 24 and s.render.fps_base == 1.0, f"{s.render.fps}")
    check("Tempo", "duracao 15 s", (s.frame_end - s.frame_start + 1) / s.render.fps == 15.0)
    marc = {m.frame: m.name for m in s.timeline_markers}
    check("Tempo", "marcadores 1/73/241 (Inicio/Desenvolvimento/Encerramento)", marc == MARCADORES, str(marc))

    # --- saida ---
    check("Saida", "1920x1080", (s.render.resolution_x, s.render.resolution_y) == (1920, 1080))
    check("Saida", "FFMPEG / MPEG4 / H264",
          s.render.image_settings.file_format == "FFMPEG" and s.render.ffmpeg.format == "MPEG4"
          and s.render.ffmpeg.codec == "H264", f"{s.render.ffmpeg.format}/{s.render.ffmpeg.codec}")

    # --- colecoes ---
    nomes = {c.name for c in bpy.data.collections}
    check("Colecoes", "Marca/Objetos_Autorais/Cenario/Cameras/Luzes", set(COLECOES) <= nomes, ", ".join(sorted(nomes)))
    check("Colecoes", "todas ligadas a cena", all(c in [x.name for x in s.collection.children] for c in COLECOES))
    check("Colecoes", "colecao raiz antiga removida", "AP1_Ibmec_Conceito" not in nomes)
    check("Colecoes", "Marca contem Palavra_Ibmec e Palavra_Ponto_i",
          {o.name for o in bpy.data.collections["Marca"].objects} == set(PALAVRA))
    check("Colecoes", "Cameras contem Cam_Principal e Alvo_Camera",
          {o.name for o in bpy.data.collections["Cameras"].objects} == {"Cam_Principal", "Alvo_Camera"})
    sol_cena = [o.name for o in s.collection.all_objects]
    check("Colecoes", "nenhum objeto solto na colecao raiz da cena", not s.collection.objects.keys())
    check("Colecoes", "Obj_Robo_Cabeca/Braco/Foguete_Chama em Objetos_Autorais",
          {"Obj_Robo_Cabeca", "Obj_Robo_Braco", "Obj_Foguete_Chama"}
          <= {o.name for o in bpy.data.collections["Objetos_Autorais"].objects}, f"{len(sol_cena)} objetos")

    # --- camera ---
    cam = O["Cam_Principal"]
    ks = faixa_keys(cam)
    check("Camera", "Cam_Principal definida e animada", s.camera == cam and ks is not None and varia(cam), str(ks))
    check("Camera", "keyframes 1..360 (push-in 1-330, hold 330-360)", ks == (1.0, 360.0))
    fc = [f for f in fcurves(cam) if f.data_path == "location" and f.array_index == 1][0]
    y330, y360 = fc.evaluate(330), fc.evaluate(360)
    check("Camera", "travada 330..360 (sem movimento)", abs(y330 - y360) < 1e-4 and abs(fc.evaluate(345) - y360) < 1e-4)
    check("Camera", "push-in continuo (aproxima ate 330)", fc.evaluate(1) < fc.evaluate(165) < y330, f"y: {fc.evaluate(1):.1f} -> {y330:.1f}")
    check("Camera", "Track To -> Alvo_Camera mantida",
          any(c.type == "TRACK_TO" and c.target and c.target.name == "Alvo_Camera" for c in cam.constraints))

    # --- elementos animados ---
    animados = [o.name for o in O if o.name != "Cam_Principal" and varia(o)]
    check("Animacao", "pelo menos 2 elementos animados alem da camera", len(animados) >= 2, f"{len(animados)}")
    check("Animacao", "inclui Ibmec ou objeto autoral",
          any(n in animados for n in ("Palavra_Ibmec", "Palavra_Ponto_i", "Obj_Robo_Cabeca", "Obj_Robo_Braco",
                                      "Obj_Foguete", "Obj_Computador")), ", ".join(animados))
    for nome in ("Palavra_Ibmec", "Palavra_Ponto_i", "Obj_Robo_Cabeca", "Obj_Robo_Braco", "Obj_Foguete",
                 "Obj_Foguete_Chama") + tuple(f"Aux_Bloco_0{i}" for i in range(1, 6)):
        check("Animacao", f"{nome} animado", nome in animados, str(faixa_keys(O[nome])))
    tela = bpy.data.materials["Mat_Obj_Computador_Tela"]
    check("Animacao", "tela do computador: emissao animada (material proprio)",
          varia(tela.node_tree) and tela.name != "MAT_Madeira_PBR" and O["Obj_Computador_Tela"].active_material == tela)
    # Ibmec legivel e parado de 214 a 360
    w = O["Palavra_Ibmec"]
    parada = True
    for fc in fcurves(w):
        if abs(fc.evaluate(214) - fc.evaluate(360)) > 1e-5 or abs(fc.evaluate(290) - fc.evaluate(360)) > 1e-5:
            parada = False
    check("Animacao", "Ibmec parada 214..360", parada)
    sc = [f for f in fcurves(w) if f.data_path == "scale"][0]
    check("Animacao", "Ibmec: escala final 1.0", abs(sc.evaluate(360) - 1.0) < 1e-6)
    # todos os keyframes com interpolacao definida (nada 'padrao' sem revisao: tipo explicito)
    tipos = {p.interpolation for o in O for fc in fcurves(o) for p in fc.keyframe_points}
    check("Interpolacao", "tipos usados", True, ", ".join(sorted(tipos)))

    # --- materiais AC05 ---
    for nome, mat in {**AUTORAIS, **PALAVRA}.items():
        m = O[nome].active_material
        check("Materiais", f"{nome}: {mat}", m is not None and m.name == mat, m.name if m else "-")
    madeira = bpy.data.materials["MAT_Madeira_PBR"]
    check("Materiais", "MAT_Madeira_PBR sem animacao", not fcurves(madeira.node_tree))
    check("Materiais", "chama com material emissivo proprio",
          O["Obj_Foguete_Chama"].active_material.name == "Mat_Foguete_Chama")

    # --- imagens ---
    usadas = [i for i in bpy.data.images if i.source == "FILE"]
    check("Imagens", "imagens externas empacotadas (sem caminhos soltos)",
          bool(usadas) and all(i.packed_file is not None for i in usadas),
          f"{sum(1 for i in usadas if i.packed_file)}/{len(usadas)} empacotadas")
    # 'Render Result' (source VIEWER) e' apenas o visualizador do Blender: nao e arquivo, nao se empacota.
    outras = [i.name for i in bpy.data.images if i.source != "FILE"]
    check("Imagens", "total = 7 arquivos + visualizador (Render Result); nenhuma orfa (0 users)",
          len(usadas) == 7 and all(i.users > 0 for i in usadas) and outras == ["Render Result"],
          f"{len(usadas)} FILE + {outras}")
    check("Imagens", "HDRI empacotado", bpy.data.images.get("hdri_studio_small_08") is not None
          and bpy.data.images["hdri_studio_small_08"].packed_file is not None)

    # --- composicao (projecao na camera; coordenadas do quadro 0..1, y para cima) ---
    s.frame_set(360)
    corpo, chama = O["Obj_Foguete_Corpo"], O["Obj_Foguete_Chama"]
    cx = ap2.uniao([ap2.caixa_tela(corpo, s), ap2.caixa_tela(chama, s)])
    cc = ap2.caixa_tela(corpo, s)
    m = 0.02
    check("Composicao", "foguete+chama inteiros dentro do quadro no frame 360 (margem 2%)",
          cx[0] >= m and cx[1] >= m and cx[2] <= 1 - m and cx[3] <= 1 - m,
          "x %.3f-%.3f  y %.3f-%.3f" % (cx[0], cx[2], cx[1], cx[3]))
    ccx, ccy = (cc[0] + cc[2]) / 2, (cc[1] + cc[3]) / 2
    check("Composicao", "corpo do foguete no terco superior direito (centro x>2/3, y>2/3)",
          ccx > 2 / 3 and ccy > 2 / 3, "centro (%.3f, %.3f)" % (ccx, ccy))
    fora = []
    for f in range(270, 361, 6):
        s.frame_set(f)
        c = ap2.uniao([ap2.caixa_tela(corpo, s), ap2.caixa_tela(chama, s)])
        if not (c[0] >= 0 and c[1] >= 0 and c[2] <= 1 and c[3] <= 1):
            fora.append(f)
    check("Composicao", "foguete dentro do quadro em todo o trecho 270-360", not fora, str(fora or "ok"))
    fz = [f for f in fcurves(O["Obj_Foguete"]) if f.data_path == "location" and f.array_index == 2][0]
    v = lambda a, b: (fz.evaluate(b) - fz.evaluate(a)) / (b - a)
    v_ini, v_fim, v_meio = v(270, 276), v(354, 360), v(318, 324)
    check("Composicao", "foguete sobe ate o fim (velocidade > 0 em 354-360, nao para no ar)", v_fim > 0.01,
          "%.4f u/frame" % v_fim)
    check("Composicao", "ease-in na partida (v 270-276 < 40% da v final)", v_ini < 0.4 * v_fim,
          "%.4f -> %.4f" % (v_ini, v_fim))
    check("Composicao", "velocidade quase constante no fim (v 318-324 / v 354-360 entre 0.95 e 1.05)",
          0.95 <= v_meio / v_fim <= 1.05, "%.3f" % (v_meio / v_fim))
    ruins = ap2.blocos_sobre_palavra(range(190, 361, 2))
    check("Composicao", "nenhum bloco sobre a Ibmec de 190 a 360 (a cada 2 frames, margem 0.8%)", not ruins,
          str(ruins[:2]) if ruins else "0 sobreposicoes")
    desc, frente = [], []
    ok_centro = True
    marca = {"Palavra_Ibmec", "Palavra_Ponto_i", "Aux_Chao"}
    for f in range(214, 361, 6):
        s.frame_set(f)
        pal = ap2.caixa_palavra(s)
        if abs((pal[0] + pal[2]) / 2 - 0.5) > 0.02:
            ok_centro = False
        for o in O:
            if o.type != "MESH" or o.name in marca or o.parent and o.parent.name in marca:
                continue
            c = ap2.caixa_tela(o, s)
            if c[4] < pal[4] and ap2.sobrepoe(c, pal) and o.name in (
                    [f"Aux_Bloco_0{i}" for i in range(1, 6)] + ["Obj_Foguete_Corpo", "Obj_Foguete_Chama"]):
                frente.append((f, o.name))
    check("Composicao", "Ibmec centralizada na horizontal de 214 a 360 (|cx-0.5| <= 0.02)", ok_centro,
          "f360: x %.3f-%.3f" % (pal[0], pal[2]))
    check("Composicao", "nada na frente da Ibmec de 214 a 360 (blocos/foguete)", not frente, str(frente[:3]) if frente else "ok")

    # --- iluminacao / emissoes ---
    check("Luz", "LUZ_Principal (Sun) e LUZ_Preenchimento (Area) da AC05",
          O["LUZ_Principal"].data.type == "SUN" and O["LUZ_Preenchimento"].data.type == "AREA")
    wn = s.world.node_tree.nodes
    check("Luz", "World: fundo cinza + HDRI + Mix por Light Path",
          all(n in wn for n in ("Background", "Environment Texture", "Mix Shader", "Light Path")))
    lim_t, lim_c = s.get("ap2_limite_tela"), s.get("ap2_limite_chama")
    check("Emissao", "limites definidos na cena (tela, chama)", lim_t is not None and lim_c is not None,
          "tela<=%s chama<=%s" % (lim_t, lim_c))
    es = bpy.data.materials["Mat_Obj_Computador_Tela"].node_tree
    pico_tela = max(p.co[1] for fc in fcurves(es) for p in fc.keyframe_points)
    check("Emissao", "tela: pico da animacao <= limite", lim_t is not None and pico_tela <= lim_t + 1e-6,
          "pico %.2f / limite %s" % (pico_tela, lim_t))
    forca = O["Obj_Foguete_Chama"].active_material.node_tree.nodes["Emission"].inputs["Strength"].default_value
    check("Emissao", "chama: Strength <= limite", lim_c is not None and forca <= lim_c + 1e-6,
          "%.2f / limite %s" % (forca, lim_c))
    check("Emissao", "palavra Ibmec sem emissao (cor da marca vem do difuso)",
          all(bpy.data.materials[n].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value == 0
              for n in ("MAT_Ibmec_PBR", "MAT_Ibmec_Ponto_PBR")))

    # --- render ---
    esperado = {"CYCLES": "CYCLES", "EEVEE": "BLENDER_EEVEE_NEXT"}[ap2.MOTOR_FINAL]
    check("Render", f"motor final = {ap2.MOTOR_FINAL} (recomendado no teste de motor)", s.render.engine == esperado,
          s.render.engine)
    check("Render", "Cycles: 64 spp, denoise OptiX", s.cycles.samples == 64 and s.cycles.denoiser == "OPTIX",
          "%d spp, %s" % (s.cycles.samples, s.cycles.denoiser))
    check("Render", "motion blur ligado (obturador %.2f)" % ap2.MB_OBTURADOR,
          s.render.use_motion_blur and abs(s.render.motion_blur_shutter - ap2.MB_OBTURADOR) < 1e-6)
    check("Render", "teste de motor salvo (8 PNG + tempos.csv)",
          os.path.isfile(os.path.join(DESTINO, "saida", "teste_motor", "tempos.csv"))
          and len([x for x in os.listdir(os.path.join(DESTINO, "saida", "teste_motor")) if x.endswith(".png")]) == 8)
    check("Render", "7 previas 960x540 salvas",
          len([x for x in os.listdir(os.path.join(DESTINO, "saida", "previas")) if x.endswith(".png")]) == 7)

    # --- tabela ---
    ordem = list(dict.fromkeys(r[0] for r in RESULT))
    RESULT.sort(key=lambda r: ordem.index(r[0]))
    larg = max(len(r[1]) for r in RESULT) + 2
    barra = "=" * (larg + 40)
    print("\n" + barra)
    print(f"VALIDACAO AP2  ({os.path.basename(BLEND)})")
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
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
