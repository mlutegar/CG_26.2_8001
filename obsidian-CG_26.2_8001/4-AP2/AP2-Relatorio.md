# AP2: Relatório (resumo)

⬅️ [[AP2]] · [[AP2-Storyboard]] · [[AP2-Animacao]] · [[AP2-Iluminacao-Render]]

Arquivo: `AP2/relatorio/AP2_relatorio.md`. Seções: 1 conceito e resumo · 2 momentos e planos · 3 propriedades animadas e interpolação ·
4 iluminação e renderização · 5 materiais e texturas da [[AC05]] · 6 desafios e soluções · 7 fontes e licenças · 8 entregáveis · 9 autoria.

Imagens: frame final, frame 214, storyboard, curvas (câmera, Ibmec, foguete) e comparação Eevee x Cycles.

![[AP2_MichelLutegar_frame_214.png]]
![[comparacao_motor.png]]

- Interpolações: Quad ease-in (quedas), Back ease-out (encaixe com overshoot), Sine ease-in-out (movimentos suaves), Bezier (câmera), Linear amostrado (foguete).
- Render: Cycles OptiX 64 spp, motion blur 0,35; Eevee ~4x mais rápido, mas sem os reflexos do robô e do metal. Final: 1953 s.
- Imagens do `.blend`: 7 de arquivo (todas empacotadas) + `Render Result` (visualizador, não conta). Nenhuma órfã.
- Principled BSDF não é Phong nem Blinn-Phong.
- Fontes: Poly Haven (brown_planks_03, studio_small_08), ambientCG (Metal009), todas CC0; fonte Krub (OFL). Sem áudio.
