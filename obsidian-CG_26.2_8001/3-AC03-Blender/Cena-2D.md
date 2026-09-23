# Cena 2D — Plano XY

⬅️ [[AC03]] · [[Painel]]

Três objetos planos na coleção `AC03_transformacoes`:

| Objeto | Primitiva | Transformação |
|---|---|---|
| `obj2d_quadrado` | Plane | translação X/Y + rotação Z (animado) |
| `obj2d_triangulo` | Plane editado (bmesh, 3 vértices) | posicionado no XY |
| `obj2d_circulo` | Mesh Circle | escala não uniforme `(1.5, 0.7)` |

O triângulo é feito com `bmesh`, substituindo os 4 vértices do plano por 3.

Próximo: [[Cena-3D]]
