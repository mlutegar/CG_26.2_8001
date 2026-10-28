# AC04 — Lambert × Phong × Blinn-Phong (Blender 4.5 LTS)

Autor: Michel Lutegar · Arquivo: `AC4/AC04_MichelLutegar.blend` (cópia da cena da AP1; original intacto).
Script: `AC4/ac04_modelos_iluminacao.py`.

## 1. Objetos e materiais
| Objeto autoral (AP1) | Malha recebedora | Material | Modelo |
|---|---|---|---|
| Obj_Computador | Obj_Computador_Corpo | MAT_Lambert | difuso, fosco |
| Obj_Robo | Obj_Robo_Corpo | MAT_Phong | difuso + especular |
| Obj_Foguete | Obj_Foguete_Corpo | MAT_BlinnPhong | difuso + especular (vetor médio) |

Subpartes (tela, mouse, olhos, peito) e a palavra Ibmec mantêm seus materiais da AP1.

## 2. Iluminação (fixa em todas as imagens comparativas)
- **LUZ_Principal** — Sun, energia 4.0, cor branca (1,1,1), rotação (50°, 0°, 35°), ângulo 1.5°.
- **LUZ_Preenchimento** — Area, energia 250 W, tamanho 8 m, cor (0.85, 0.9, 1.0), posição (-5, -6, 5), Track To no `Alvo_Camera`.
- Câmera `Cam_Principal` inalterada (nos closes de comparação só muda a posição/lente, igual para a luz).
- Render: Cycles, denoise ligado. Coleções: `Luzes`, `Materiais_AC04` sob `AP1_Ibmec_Conceito`.

## 3. Valores dos materiais (Principled BSDF)
| Material | Base Color (RGB) | Roughness | Specular IOR Level | Metallic |
|---|---|---|---|---|
| MAT_Lambert | (0.20, 0.35, 0.80) azul | 1.0 | 0.0 | 0 |
| MAT_Phong | (0.05, 0.65, 0.45) verde | 0.20 | 0.5 | 0 |
| MAT_BlinnPhong | (0.80, 0.08, 0.08) vermelho | 0.10 | 0.8 | 0 |

(No Blender 4.5 o controle é *Specular IOR Level*, usado no lugar de "Specular".)

## 4. Comparação observada
Ver `AC04_comparacao.png` (três closes, mesma luz) e `AC04_render_final.png`.
- **Lambert (computador):** superfície totalmente fosca; só variação de tom conforme o ângulo entre normal e luz (N·L), sem ponto de brilho. Sombras suaves e uniformes.
- **Phong (robô):** brilho especular discreto e relativamente espalhado nas bordas/chanfros; aparência de plástico semi-polido.
- **Blinn-Phong (foguete):** highlight mais concentrado e intenso ao longo do corpo curvo; aparência polida/vernizada. Entre Phong e Blinn-Phong a diferença é sutil, porque as duas configurações usam rugosidade baixa; o que mais as separa aqui é rugosidade (0.2 → 0.1) e intensidade especular (0.5 → 0.8).
- **Rugosidade:** quanto menor, menor e mais intenso o highlight; rugosidade 1.0 espalha a reflexão a ponto de sumir.
- **Ângulo da luz:** em `AC04_teste_angulo.png` a luz foi girada para (25°, 0°, -60°): os highlights mudam de posição no foguete e no robô e as sombras trocam de lado, enquanto o computador só muda de tom. A luz foi restaurada à configuração da seção 2 antes do render final e do salvamento.

## 5. Nota técnica — aproximações
O Principled BSDF do Blender 4.5 é um shader baseado em princípios físicos (distribuição GGX, Fresnel, conservação de energia). Seus parâmetros **não implementam literalmente** as equações clássicas de Phong, (R·V)ⁿ, nem de Blinn-Phong, (N·H)ⁿ. As configurações acima de rugosidade e especular são **aproximações visuais** para comparar o comportamento (fosco × polido, tamanho do highlight). Para o Lambert, o nó Diffuse BSDF seria uma alternativa direta da componente difusa pura.

## Entregáveis
`AC04_MichelLutegar.blend`, `AC04_render_final.png`, `AC04_comparacao.png`, `AC04_teste_angulo.png`, este relatório.
