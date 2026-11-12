# AP2 — Iluminação, texturas em movimento e motor de render

⬅️ [[AP2]] · [[AP2-Animacao]] · [[AP2-Script-Base]] · base de luz: [[AC04-Iluminacao]] · materiais: [[AC05-Materiais]] · UV: [[AC05-Texturas-UV]]

## Iluminação final
Parte da AC04/AC05: `LUZ_Principal` (Sun 4.0), `LUZ_Preenchimento` (Area 250), fundo cinza (0.32, 0.34, 0.40) e HDRI `hdri_studio_small_08` só em raios glossy (Cycles).
- **Rim light** (`LUZ_Rim`, Area 7×1.2, atrás/acima da palavra): testado e **descartado** (`RIM = False`). Frame 300, 960×540: luminância média das letras 0.437→0.449 e do fundo 0.534→0.540; o contraste letra×fundo não melhorou (0.097→0.091). Não melhora a leitura.
- **Emissão** (medida em Eevee e Cycles; o AgX dessatura valores altos para branco/pêssego):

| Item | Antes | RGB médio medido antes | Agora |
|---|---|---|---|
| Tela (pico / regime) | 1.8 | (0.64, 0.74, 0.87), lavado | 0.8 / 0.64 → ≈(0.5, 0.6, 0.75) |
| Chama | 6.0 | (0.96, 0.83, 0.73), quase branca | 1.2 → laranja ≈(0.74, 0.58, 0.30) nos frames de teste |

  Limites gravados na cena (`ap2_limite_tela = 0.8`, `ap2_limite_chama = 1.2`) e checados no `validar_ap2.py`. Nenhum pixel com canal ≥ 0.98 nos frames testados.
- **Cores da marca** (frames 200/300/360, 1920×1080, só dentro do retângulo da palavra): azul médio (0.24, 0.33, 0.50) no Cycles e (0.22, 0.31, 0.46) no Eevee, máximo 0.77, 0% estourado, 0% escuro (< 0.08). Ponto do i laranja (0.74, 0.58, 0.30), sem estouro. No frame 1 a palavra ainda está escalada a 0.01 (entrada começa no 90).

## Robô espelhado no Eevee Next
Solução testada: World com `Light Path → Is Camera Ray` (câmera = cinza; demais raios = HDRI × 0.5) + raytracing de reflexos (`use_raytracing`, método SCREEN, roughness máx 0.6). No Cycles o World da AC05 (Is Glossy Ray) é mantido (`configurar_luz`).
- HDRI 0.3–0.5 deixa o robô e o foguete **quase pretos**; 3.0 aproxima o brilho mas lava o difuso (palavra azul clara, chão claro). Sun threshold 1000 e probe 2048 não mudaram nada.
- **Mudança perceptível na luz difusa** (frame 300, luminância média na tela): chão 0.568 (fiação AC05 no Eevee) → 0.503 (HDRI 0.5) → 0.472 (0.3); Cycles 0.530. Robô 0.41 → 0.34. Is Camera Ray escurece ~10% a cena no Eevee e mesmo assim não dá os reflexos nítidos do Cycles.

![[robo_eevee_vs_cycles.png]]
(esq.: Eevee Next, HDRI 1.0; dir.: Cycles. O Cycles reflete letras e luzes do estúdio; o Eevee fica liso e escuro.)

## Texturas em movimento (Cycles, recortes em tamanho real)
Foguete 270/315/360 e computador 1/200/360 em `AP2/saida/texturas_movimento/`.
- Escala do metal e da madeira coerente entre frames; **sem costura e sem esticamento** (as tábuas da base têm juntas intencionais). Brilho do metal estável e madeira sem moiré mesmo no plano aberto (frame 1). Nenhuma correção de UV/Mapping foi necessária.
- **Motion blur ligado** (obturador 0.35). Nitidez (gradiente médio) da palavra no 214: idêntica com e sem blur; foguete no 300: −0.7% (Eevee) / −2.6% (Cycles); ponto do i em queda (180): −18% / −12% (só enquanto cai; pousa nítido no 198). Câmera: sem efeito mensurável. Mantido.

![[tex_foguete_f270.png]] ![[tex_foguete_f315.png]] ![[tex_foguete_f360.png]]
![[tex_computador_f001.png]] ![[tex_computador_f200.png]] ![[tex_computador_f360.png]]

## Teste de motor (1920×1080, RTX 3050)
Cycles: OptiX GPU, 64 spp, denoise OptiX. Tempo = render + gravação do PNG, depois de 1 frame de aquecimento (compila shaders/kernels: ~2.5 s Eevee, ~4.8 s Cycles). Dados em `saida/teste_motor/tempos.csv`.

| Frame | Motor | Tempo | Observação |
|---|---|---|---|
| 1 | Eevee Next | 1.3 s | Robô/foguete escuros |
| 1 | Cycles OptiX | 4.6 s | Robô espelhado nítido |
| 200 | Eevee Next | 1.4 s | Metal sem reflexos do entorno |
| 200 | Cycles OptiX | 5.9 s | Reflexos do HDRI e da palavra no robô |
| 300 | Eevee Next | 1.5 s | Foguete preto |
| 300 | Cycles OptiX | 6.5 s | Metal escovado com realces; chão com reflexo |
| 360 | Eevee Next | 1.5 s | Foguete/chama legíveis, metal chapado |
| 360 | Cycles OptiX | 6.6 s | Mesmo enquadramento, material melhor |

![[motor_eevee_next_f300.png]] ![[motor_cycles_optix_64spp_f300.png]]

**Recomendação: Cycles OptiX 64 spp** (`MOTOR_FINAL = "CYCLES"`). O Eevee é ~4× mais rápido (média 1.4 s → ~8.5 min para 360 frames), mas o robô espelhado (peça central) e o metal escovado perdem o que a AC05 construiu. Marca (azul/laranja) e madeira ficam equivalentes. Cycles: média 5.9 s → **~35 min para 360 frames** (~40 min com margem). Prazo 18/11: folga grande.

## Prévias
7 prévias 960×540 com Cycles (≈2 s cada): ![[previa_001.png]] ![[previa_360.png]]

## P10 — Chama, teste rápido e render final
⬅️ [[AP2]] · [[AP2-Animacao]]
- **Chama**: malha em gota + `Mat_Foguete_Chama` com gradiente em Z do objeto (amarelo → laranja → vermelho), Emission × Transparent BSDF (opacidade cai na ponta) e Noise 4D por driver; flicker Noise na escala mantido. Strength 1.2 (limite inalterado).
- **Teste rápido** (Cycles 960×540, 16 spp, 1–360): 365 s. Sem saltos, cortes ou colisões (checado por bbox e vértices).
- **Final** (Cycles OptiX 1920×1080, 64 spp, MB 0.35): 1953 s (32 min 33 s), 360/360 PNG em `saida/frames/`, MP4 H.264 CRF 14 via ffmpeg.
