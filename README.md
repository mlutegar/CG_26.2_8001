# CG_26.2_8001: Computação Gráfica

Repositório das atividades da disciplina **Computação Gráfica**, turma **8001**, semestre **2026.2**
(aluno: Michel Lutegar). Cada pasta tem um `enunciado.md` com o enunciado da atividade.

## Atividades

| Atividade | Tema | Ferramenta | Pasta | Entregáveis principais |
|---|---|---|---|---|
| AC1 | Áreas da Computação Visual (síntese, processamento, visão, visualização) | Python 3.12 | [AC1](AC1/) | [relatório](AC1/relatorio/AC01_relatorio.md), 4 scripts em `01_` a `04_`, `executar_tudo.py` |
| AC2 | Transformações geométricas 2D (matrizes homogêneas) | Python 3.12, Matplotlib | [AC2](AC2/) | [relatório](AC2/relatorio/AC02_relatorio.md), `transformacoes.py`, 10 figuras em `saida/` |
| AC3 | Transformações 2D e 3D, animação por keyframes ("Parque Geométrico") | Blender 4.5 LTS | [AC3](AC3/) | [relatório](AC3/relatorio/AC03_relatorio.md), `AC03_parque_geometrico.py` |
| AC4 | Modelos de iluminação: Lambert, Phong e Blinn-Phong | Blender 4.5 LTS | [AC4](AC4/) | [README](AC4/README.md), `ac04_modelos_iluminacao.py`, `.blend` e renders |
| AC5 | Materiais PBR e texturas (UVs, cor base, rugosidade, normal) | Blender 4.5 LTS | [AC5](AC5/) | `AC05_MichelLutegar.blend`, `ac05_materiais_texturas.py`, `validar_ac05.py`, relatório |
| AP1 | Cena-conceito 3D "Ibmec: Construindo o Futuro" | Blender 4.5 LTS | [AP1](AP1/) | [relatório com storyboard](AP1/relatorio/Relatorio_AP1_MichelLutegar.md), `.blend` e 5 imagens em `saida/` |
| AP2 | Animação final "Ibmec em 15 segundos" | Blender 4.5 LTS (Cycles OptiX) | [AP2](AP2/) | vídeo, `.blend`, relatório, storyboard, checklist |

## Destaque: AP2

Peça de 15 s (360 frames, 24 fps, 1920x1080, H.264) que integra a cena da AP1, a iluminação da AC4 e os
materiais da AC5. Validação: `validar_ap2.py` 65/65 OK e `validar_ac05.py` 62/62 OK.

- Vídeo: [AP2/AP2_MichelLutegar.mp4](AP2/AP2_MichelLutegar.mp4)
- Relatório: [AP2/relatorio/AP2_relatorio.md](AP2/relatorio/AP2_relatorio.md)
- Storyboard: [AP2/storyboard/AP2_storyboard.png](AP2/storyboard/AP2_storyboard.png)
- Checklist de entrega: [AP2/CHECKLIST_ENTREGA.md](AP2/CHECKLIST_ENTREGA.md)
- Como rodar a AP2: [AP2/README.md](AP2/README.md)

Frame final (360):

![Frame final da AP2](AP2/saida/AP2_MichelLutegar_frame_final.png)

## Requisitos

- **AC1 e AC2:** Python 3.12 e as dependências de [requirements.txt](requirements.txt)
  (NumPy, SciPy, Matplotlib, scikit-image, OpenCV e Pillow).
- **AC3 em diante:** Blender 4.5 LTS. Executável no Windows:
  `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`
- **AP2 (render final):** GPU NVIDIA com OptiX e `ffmpeg` no PATH.

### Instalação das dependências Python

```bash
python -m pip install -r requirements.txt
```

Nota: use `python -m pip` e não `pip` direto. Em máquinas com mais de um Python instalado, o comando `pip`
pode apontar para outra versão e instalar os pacotes fora do Python 3.12. Com `python -m pip` o pacote vai
para o mesmo interpretador que vai executar os scripts.

## Como rodar

Na raiz do repositório.

**AC1 e AC2 (Python):**

```bash
python AC1/executar_tudo.py
python AC2/executar_ac2.py
```

**AC3 a AP2 (Blender, PowerShell):**

```powershell
$B = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

# AC3: abrir AC3\AC03_parque_geometrico.py na aba Scripting do Blender e executar
& $B --background --python AC4\ac04_modelos_iluminacao.py        # AC4
& $B --background --python AC5\ac05_materiais_texturas.py        # AC5: gerar o .blend
& $B --background --python AC5\validar_ac05.py                   # AC5: validar
& $B --background --python AP1\ap1_ibmec_conceito.py             # AP1
```

**AP2 (flags por variável de ambiente):**

```powershell
# gerar o .blend
& $B --background --python AP2\ap2_ibmec_final.py

# render de teste (7 prévias 960x540 em AP2\saida\previas)
$env:AP2_RENDER_TESTE = "1"; & $B -b --python AP2\ap2_ibmec_final.py; Remove-Item Env:AP2_RENDER_TESTE

# render final (360 PNG 1920x1080 em AP2\saida\frames, cerca de 33 min numa RTX 3050) e montagem do MP4
$env:AP2_RENDER_SEQ_FINAL = "1"; & $B -b --python AP2\ap2_ibmec_final.py; Remove-Item Env:AP2_RENDER_SEQ_FINAL
ffmpeg -framerate 24 -i AP2\saida\frames\f_%04d.png -c:v libx264 -crf 14 -pix_fmt yuv420p AP2\AP2_MichelLutegar.mp4

# validar
& $B -b --python AP2\validar_ap2.py
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration -of default=nw=1 AP2\AP2_MichelLutegar.mp4
```

Atenção: gerar o `.blend` e renderizar sobrescreve `AP2_MichelLutegar.blend` e `AP2_MichelLutegar.mp4`.
Outras flags (teste rápido, comparação de motor, texturas em movimento) estão em [AP2/README.md](AP2/README.md).

## Estrutura de pastas

```
CG_26.2_8001/
├── README.md · requirements.txt
├── obsidian-CG_26.2_8001/   vault Obsidian com anotações interligadas
├── AC1/ · AC2/              Python (relatorio/, saida/)
├── AC3/ · AC4/ · AC5/       Blender (scripts, .blend, relatorio/, saida/)
├── AP1/                     cena-conceito (assets/, relatorio/, saida/)
└── AP2/                     animação final (.blend, .mp4, relatorio/, storyboard/, saida/)
```

Anotações do curso: abra a pasta [obsidian-CG_26.2_8001](obsidian-CG_26.2_8001/) como vault no Obsidian.
O ponto de entrada é o [Painel](obsidian-CG_26.2_8001/0-Painel/Painel.md).

## Fontes e licenças dos recursos externos

| Recurso | Fonte | Licença | Uso |
|---|---|---|---|
| `brown_planks_03` (textura) | [Poly Haven](https://polyhaven.com/a/brown_planks_03) | CC0 | Madeira do computador (AC5, AP2) |
| `studio_small_08` (HDRI) | [Poly Haven](https://polyhaven.com/a/studio_small_08) | CC0 | Reflexos (AC5, AP2) |
| `Metal009` (textura) | [ambientCG](https://ambientcg.com/a/Metal009) | CC0 | Metal do foguete (AC5, AP2) |
| Fonte **Krub SemiBold** | [Google Fonts](https://fonts.google.com/specimen/Krub), Cadson Demak | SIL Open Font License 1.1 (confirmar na página da fonte; o arquivo de licença não está no repositório) | Letras "bmec" (AP1, AP2) |
| `LOGO_IBMEC_3D.blend` | Material da disciplina e marca Ibmec | Marca registrada, uso acadêmico | Malhas do "I" e do ponto (AP1) |

`AP1/assets/fonts/` contém a família Lagu Sans (fonte original do logotipo). Ela não foi usada na renderização
e a licença não está identificada. Detalhes das texturas em [AC5/texturas/FONTES.md](AC5/texturas/FONTES.md).
