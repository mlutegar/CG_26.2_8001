# AP2 — Script base

⬅️ [[AP2]] · [[AP2-Animacao]]

`AP2/ap2_ibmec_final.py` (Blender 4.5): `blender -b --python AP2/ap2_ibmec_final.py`

| Variável | Efeito |
|---|---|
| (nenhuma) | só gera o `.blend` |
| `AP2_DESTINO` | pasta de saída (padrão `AP2/`) |
| `AP2_RENDER_TESTE=1` | 7 prévias 960x540 (motor final) em `saida/previas/` |
| `AP2_RENDER_MOTOR=1` | teste de motor 1/200/300/360 em `saida/teste_motor/` + `tempos.csv` |
| `AP2_RENDER_TEXTURAS=1` | recortes Cycles em `saida/texturas_movimento/` |
| `AP2_RENDER_RAPIDO=1` | sequência 960x540 16 spp em `saida/teste_rapido/` |
| `AP2_RENDER_SEQ_FINAL=1` | 360 PNG 1920x1080 Cycles 64 spp em `saida/frames/` (depois ffmpeg libx264 CRF 14 gera o MP4 entregue) |
| `AP2_RENDER_FINAL=1` | vídeo `AP2_<AUTOR>.mp4` H.264 (`AP2_MOTOR` = CYCLES ou EEVEE, padrão `MOTOR_FINAL`; `AP2_FRAMES`, `AP2_ESCALA`) |

- Coleções: Marca, Objetos_Autorais, Cenario, Cameras, Luzes.
- Marcadores: 1 Inicio · 73 Desenvolvimento · 241 Encerramento.
- Robô: malha da AC05 tinha 18 ilhas soltas → separadas em `Obj_Robo_Cabeca` e `Obj_Robo_Braco` (mesmo MAT_Espelho_PBR).
- Chama do foguete: `Obj_Foguete_Chama` + `Mat_Foguete_Chama` (emissivo).
- Tela do computador: `Mat_Obj_Computador_Tela` (material próprio) com emissão animada; `MAT_Madeira_PBR` intacto.
- Validação: `AP2/validar_ap2.py`. Curvas: `AP2/gerar_curvas.py`.
