# AC05: Materiais

⬅️ [[AC05]] · [[Painel]] · ver [[AC05-Texturas-UV]] · antes: [[AC04-Materiais]]

| Objeto | Material | Base Color | Roughness | Metallic |
|---|---|---|---|---|
| Obj_Robo | MAT_Espelho_PBR | (0.95, 0.95, 0.95) | 0.02 | 1 |
| Obj_Computador | MAT_Madeira_PBR | textura sRGB | textura Non-Color | 0 |
| Obj_Foguete | MAT_Metal_Escovado_PBR | textura sRGB | textura remapeada 0.30 a 0.50 | 1 |
| Palavra Ibmec | MAT_Ibmec_PBR | azul-marinho da marca | 0.45 | 0 |
| Ponto do "i" | MAT_Ibmec_Ponto_PBR | laranja da marca | 0.45 | 0 |

- Robô espelhado liga a palavra, o chão e os demais objetos pelos reflexos; computador em madeira
  lembra a base sólida do conceito de [[AP1]]; foguete metálico escovado dá o ar de futuro.
- A palavra Ibmec não recebe textura, normal nem bump.
- Iluminação da [[AC04-Iluminacao]] mantida. Único acréscimo: HDRI Studio Small 08 (Poly Haven, CC0, Sergej Majboroda)
  no World, usado só em raios glossy (Light Path > Is Glossy Ray misturando o cinza da AC04 e o HDRI).
  Câmera e luz difusa veem o mesmo mundo da AC04, então a iluminação dos objetos não muda.
- As faixas `Refletor_1..3` foram testadas junto do HDRI e removidas: estouravam o rosto do robô.
