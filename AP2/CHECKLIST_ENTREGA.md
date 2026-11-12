# AP2: checklist de entrega

Auditoria item por item do [enunciado](enunciado.md). Resultado: **todos os itens OK, nenhum FALTA**.

Conferências executadas (Blender 4.5.14 LTS, 2026-11-12):

- `validar_ap2.py`: **65/65 OK** (`blender -b --python AP2\validar_ap2.py`)
- `AC5/validar_ac05.py`: **62/62 OK** (`blender -b --python AC5\validar_ac05.py`)
- `ffprobe AP2/AP2_MichelLutegar.mp4`: `h264` (High), 1920x1080, `yuv420p`, 24/1 fps, 360 frames, 15,000 s

Sigla do relatório: R = [relatorio/AP2_relatorio.md](relatorio/AP2_relatorio.md). V = `validar_ap2.py`.

## Continuidade das etapas anteriores

| Item | Evidência | Status |
|---|---|---|
| Cópia da AC05 salva como `AP2_NomeSobrenome.blend`; AP1, AC04 e AC05 preservadas | `AP2/AP2_MichelLutegar.blend`; o script abre `AC5/AC05_MichelLutegar.blend` só para leitura (`AP2/README.md`); AC05 passa 62/62 | OK |
| Conceito, composição e momentos do storyboard da AP1 mantidos | R seção 2, "Mudanças em relação ao storyboard da AP1"; marcadores 1/73/241 (V, [Tempo]) | OK |
| Palavra Ibmec principal, legível, sem ocultação | V: Ibmec parada 214..360, escala final 1.0, centralizada, nada na frente, sem emissão; R seção 4 (marca) | OK |
| Três objetos autorais mantidos e participando | V: Obj_Robo_Cabeca/Braco, Obj_Foguete, tela do computador animados; R seção 1 e 2 | OK |
| Materiais e mapas da AC05 reaproveitados e ajustados | V [Materiais]; R seção 5 | OK |
| Principled BSDF não descrito como Phong/Blinn-Phong | R seção 4, "Sobre os modelos de iluminação"; `AP2/README.md` | OK |

## Requisitos de produção

| Item | Evidência | Status |
|---|---|---|
| **1. Planejamento e continuidade**: conceito, storyboard e papel dos objetos revistos | R seções 1 e 2; `storyboard/AP2_storyboard.png` | OK |
| 1. Momentos com ação, duração e enquadramento | R seção 2, tabela de momentos | OK |
| 1. Marca legível nos momentos principais | V [Composicao]: Ibmec centralizada 214..360, nenhum bloco sobre a palavra de 190 a 360 | OK |
| 1. Nomes identificáveis (objetos, câmeras, luzes, materiais) e cena organizada | V [Colecoes]: Marca, Objetos_Autorais, Cenario, Cameras, Luzes; Cam_Principal, LUZ_Principal, LUZ_Preenchimento, `MAT_*` | OK |
| **2. Animação** 360 frames, 24 fps, frames 1 a 360 | V [Tempo]: 1-360, 24 fps, 15 s | OK |
| 2. Câmera e pelo menos dois elementos animados, um deles Ibmec ou objeto autoral | V [Camera] e [Animacao]: 11 elementos animados; Palavra_Ibmec, robô e foguete | OK |
| 2. Propriedades adequadas (posição, rotação, escala, emissão) | R seção 3, tabela de propriedades | OK |
| 2. Keyframes e revisão de timing, espaçamento e interpolação no Graph Editor | R seção 3 (justificativa por interpolação); `saida/curvas/` (3 PNG e `tabela_animacao.md`) | OK |
| 2. Sem movimentos involuntários, mudanças bruscas ou colisões visuais | V [Composicao]: câmera travada 330..360, foguete com velocidade constante no fim, 0 sobreposições sobre a marca | OK |
| **3. Iluminação** que mantém legibilidade e valoriza superfícies | V [Luz] e [Emissao]; R seção 4 | OK |
| 3. PBR da AC05 em três objetos; Ibmec com material da identidade visual | V [Materiais]: robô `MAT_Espelho_PBR`, computador `MAT_Madeira_PBR`, foguete `MAT_Metal_Escovado_PBR`, Ibmec `MAT_Ibmec_PBR` e `MAT_Ibmec_Ponto_PBR` | OK |
| 3. Texturas verificadas em movimento | R seção 5, "Verificação em movimento"; `saida/texturas_movimento/` | OK |
| 3. Mapas corretos: cor base sRGB, rugosidade e normal Non-Color, Normal Map | R seção 5; `validar_ac05.py` 62/62 (espaço de cor e nó Normal Map) | OK |
| 3. Imagens externas empacotadas | V [Imagens]: 7/7 empacotadas, nenhuma órfã, HDRI empacotado | OK |
| **4. Renderização**: Eevee ou Cycles no Blender 4.5 LTS | V [Render]: Cycles, 64 spp, denoise OptiX; R seção 4 (comparação Eevee x Cycles) | OK |
| 4. Resolução, fps e intervalo configurados | V [Saida] e [Tempo]: 1920x1080, 24 fps, 1 a 360 | OK |
| 4. MP4 H.264, com testes curtos antes | ffprobe: h264, 15,000 s; V: 7 prévias 960x540 e teste de motor salvos; `AP2/README.md` (render de teste e teste rápido) | OK |
| 4. Vídeo assistido integralmente | R seção 4 (conferência com ffprobe) e folhas de contato `saida/folha_contato_final.png`. A conferência visual do vídeo é feita por você, não por script | OK |

## Requisitos técnicos

| Item | Evidência | Status |
|---|---|---|
| 15 s, 24 fps, 360 frames | ffprobe: 24/1, 360 frames, 15,000 s | OK |
| Câmera e dois elementos animados, com Ibmec ou objeto autoral | V [Camera] e [Animacao] | OK |
| Ibmec e três objetos autorais preservados e reconhecíveis | V [Colecoes] (Marca e Objetos_Autorais); frames `saida/AP2_MichelLutegar_frame_214.png` e `frame_final.png` | OK |
| PBR e texturas da AC05 nos objetos autorais | V [Materiais] | OK |
| Iluminação de apoio à narrativa | V [Luz] | OK |
| Animação completa renderizada e exportada em MP4 H.264 | `AP2/AP2_MichelLutegar.mp4`, ffprobe | OK |
| `.blend` organizado, recursos empacotados | V [Colecoes] e [Imagens] | OK |

## Entregáveis

| Item | Evidência | Status |
|---|---|---|
| `AP2_NomeSobrenome.blend` | [AP2_MichelLutegar.blend](AP2_MichelLutegar.blend) | OK |
| `AP2_NomeSobrenome.mp4`, 15 s, 24 fps | [AP2_MichelLutegar.mp4](AP2_MichelLutegar.mp4) | OK |
| Pelo menos uma imagem renderizada | [frame final](saida/AP2_MichelLutegar_frame_final.png) e [frame 214](saida/AP2_MichelLutegar_frame_214.png) | OK |
| Storyboard atualizado | [AP2_storyboard.png](storyboard/AP2_storyboard.png) | OK |
| Relatório `.md` | [AP2_relatorio.md](relatorio/AP2_relatorio.md) | OK |

## Os 7 tópicos do relatório

| # | Tópico exigido | Seção do relatório | Status |
|---|---|---|---|
| 1 | Título, conceito e resumo da sequência | 1 | OK |
| 2 | Momentos ou planos e ações animadas | 2 | OK |
| 3 | Propriedades animadas e decisões de timing e interpolação | 3 | OK |
| 4 | Configuração geral de iluminação e renderização | 4 | OK |
| 5 | Materiais e texturas reaproveitados ou ajustados da AC05 | 5 | OK |
| 6 | Desafios encontrados e soluções adotadas | 6 | OK |
| 7 | Fontes e licenças de recursos externos | 7 (fonte tipográfica corrigida para Krub SemiBold) | OK |

## Observação sobre a fonte tipográfica

As letras "bmec" foram criadas na AP1 com **Krub SemiBold** (`Krub-SemiBold.ttf`, instalada em `%LOCALAPPDATA%\Microsoft\Windows\Fonts`) e convertidas em malha. O `.blend` da AP2 não contém objetos de texto nem fontes, então não depende da fonte instalada. A licença (SIL OFL 1.1) não está no repositório; confirmar em https://fonts.google.com/specimen/Krub (aba License).
