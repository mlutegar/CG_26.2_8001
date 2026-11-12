# AP2 — Animação

⬅️ [[AP2]] · [[AP2-Script-Base]] · [[AP2-Iluminacao-Render]] · conceito em [[Animacao-Keyframes]] · [[AP1-Storyboard]]

- Câmera: push-in 1→330 (Bezier, ease in/out), travada 330–360. Track To em `Alvo_Camera` (fixo em **0,0,1.4**; era 0,0,2 — o P09 baixou o alvo para a Ibmec ficar mais centrada na vertical: centro do retângulo da palavra ≈ y 0.44).
- Ibmec: sobe+escala 90–190, pulso 190–214, parada até 360. Centralizada na horizontal (x 0.263–0.737 no 360).
- Ponto do i: queda 150–198 com leve afundamento (overshoot).
- Robô: cabeça olha o computador, vira p/ a palavra 200–230; braço acena 250–290.
- Computador: tela acende 120–150 (emissão, pico 0.8 — ver [[AP2-Iluminacao-Render]]).
- Blocos: queda escalonada 1–72 (mantida). **P09:** posições finais mudaram — 03, 04 e 05 saíram da frente da palavra.

| Bloco | (x, y) antes | (x, y) agora |
|---|---|---|
| 01 | (-4.2, -0.7) | igual |
| 02 | (4.1, -0.9) | igual |
| 03 | (-1.6, -1.7) | (-3.6, -2.0) |
| 04 | (1.8, -1.6) | (2.0, -3.5) |
| 05 | (0.1, -2.1) | (-4.4, -3.0) |

Critério: nenhum retângulo de bloco (projetado na câmera, bound_box) toca o retângulo da Ibmec em 190–360 (margem 0.8% do quadro). O `validar_ap2.py` confere a cada 2 frames.

## Foguete (redesenhado no P09)
- Escala 0.45 (base mantida no chão: origem z 2.35 → 1.31). Chama acende em 250, alongamento final 1.25.
- Decolagem 270→360: origem (3.9, 0.2, 1.31) → (4.2, 0.2, 3.46); inclina 0.10 rad para +X.
- Perfil: **ease-in** (parábola) 270→306 e **velocidade constante** 306→360 (0.0299 u/frame; razão v318/v354 = 1.000). São 16 keyframes lineares (a cada 6 frames): a curva de velocidade aparece em degraus de 6 frames, imperceptível a 24 fps.
- Frame 360: corpo+chama em x 0.795–0.864, y 0.520–0.949 (inteiro no quadro); centro do corpo (0.83, 0.81) = terço superior direito. A ponta da chama desce até y 0.52 (a chama invade o terço médio, o corpo não).

![[curvas_camera.png]]
![[curvas_ibmec.png]]
![[curvas_foguete.png]]
