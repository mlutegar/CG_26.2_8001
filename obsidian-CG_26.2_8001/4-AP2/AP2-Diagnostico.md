# AP2 — Diagnóstico (P07)

⬅️ [[AP2]] · [[Painel]] · base: [[AC05]] · [[AP1-Storyboard]] · [[Plano-AP2]]

Resumo (detalhes na resposta do prompt P07):
- Enunciado oficial salvo em `AP2/enunciado.md`; o antigo virou `AP2/enunciado_anterior.md`.
- **Achado principal:** `AP2/ap2_ibmec_final.py` é cópia de uma AP1 antiga (Livro/Torre/Foguete). A AP1/AC05
  vigentes usam **Robô/Computador/Foguete**. O vídeo atual não mostra os objetos corretos nem os materiais da AC05.
- AC05 (`AC5/AC05_MichelLutegar.blend`): sem keyframes, Cycles, imagens empacotadas.
- Benchmark (RTX 3050, 720p, cena AC05): Cycles GPU OptiX 96 spp ≈ 9,9 s/frame; Eevee 32 spp ≈ 1,2 s/frame.
- Recomendação: **novo script AP2 que abre a AC05** (não refatorar o atual) + render Cycles GPU.
