# AP2: Ibmec em 15 segundos

⬅️ [[Painel]] · base: [[AC05]] (cena, materiais, UVs) · [[AP1]] (conceito) · [[AC04]] (luz)

Peça final de 15 s (frames 1 a 360, 24 fps, 1920x1080, H.264). `AP2/ap2_ibmec_final.py` abre
`AC5/AC05_MichelLutegar.blend` (só leitura), organiza, anima e salva `AP2/AP2_MichelLutegar.blend`.

## Entregáveis
- Relatório: `AP2/relatorio/AP2_relatorio.md` (resumo em [[AP2-Relatorio]])
- Vídeo: `AP2/AP2_MichelLutegar.mp4` (H.264, 15,000 s, 360 frames, 7,3 MB, sem áudio)
- Storyboard: `AP2/storyboard/AP2_storyboard.png` (ver [[AP2-Storyboard]])
- Blend: `AP2/AP2_MichelLutegar.blend` · Frames: `AP2/saida/AP2_MichelLutegar_frame_final.png`, `..._frame_214.png`

![[AP2_MichelLutegar_frame_final.png]]

## Notas
- [[AP2-Diagnostico]]: por que refazer (P07)
- [[AP2-Script-Base]]: script, flags, coleções, marcadores
- [[AP2-Animacao]]: câmera, elementos, interpolação, curvas
- [[AP2-Iluminacao-Render]]: luz final, emissões, texturas em movimento, motor
- [[AP2-Storyboard]]: storyboard atualizado e mudanças em relação à AP1
- [[AP2-Relatorio]]: resumo do relatório final

## Estado
- [x] P08 a P10: script, animação, composição, luz, motor (Cycles OptiX), render final
- [x] P11: relatório, storyboard, READMEs, vault; `validar_ap2.py` 65/65 e `validar_ac05.py` 62/62 OK
