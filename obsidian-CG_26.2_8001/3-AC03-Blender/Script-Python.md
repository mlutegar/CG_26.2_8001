# Script Python

⬅️ [[AC03]] · [[Painel]]

`AC3/AC03_parque_geometrico.py` — roda na aba **Scripting** do Blender 4.5 LTS.

Faz por código: cria a coleção `AC03_transformacoes`, os 6 objetos, aplica
transformações, define hierarquia, insere keyframes, adiciona câmera + luz e
configura o render.

Pontos-chave:
- `bpy.ops.mesh.primitive_*_add(...)` cria as primitivas.
- `bmesh` edita o plano para virar triângulo.
- `math.radians(graus)` converte para radianos em `rotation_euler`.
- `obj.keyframe_insert(data_path=..., frame=...)` grava a animação.
- Parte **manual** (exigida): ajuste com `G`/`R`/`S` + câmera + render (F12).

Próximo: [[Questoes-Teoricas]]
