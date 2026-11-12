# AC05: Texturas e UV

⬅️ [[AC05]] · [[Painel]] · ver [[AC05-Materiais]]

## Texturas (todas CC0, 1K)
| Textura | Fonte | Uso |
|---|---|---|
| brown_planks_03 | Poly Haven (Rob Tuytel) | madeira do computador |
| Metal009 | ambientCG | metal escovado do foguete |

## Ligações (madeira e metal)
- Base Color (sRGB) -> Base Color
- Roughness (Non-Color) -> Roughness (no metal passa por Map Range 0.30 a 0.50)
- Normal (Non-Color) -> Normal Map (Tangent Space) -> Normal
- Texture Coordinate (UV) -> Mapping (escala) alimenta as três imagens

## UV (`UV_AC05`)
- **Computador:** Cube Projection, porque a malha é formada por caixas.
- **Foguete:** unwrap Angle Based com seams marcadas via bmesh (arestas vivas e uma linha no lado de trás, oposto à câmera), porque mistura cilindro, cone e aletas. A emenda vertical visível do Smart UV Project sumiu do enquadramento. 100% das faces entre 0.5x e 2x da densidade mediana.
- Escala real pelo nó Mapping: madeira 1.45, metal 7.34. Imagens empacotadas no `.blend`.

## Capturas (geradas por `AC5/capturas_ac05.py`)
Shader Editor de `MAT_Madeira_PBR`:

![[AC05_shader_editor.png]]

UV Editor de `Obj_Computador_Corpo` (todas as faces selecionadas) e layout exportado:

![[AC05_uv_editor.png]]

![[AC05_uv_layout.png]]
