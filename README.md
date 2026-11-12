# CG_26.2_8001 — Computação Gráfica

Repositório da disciplina, organizado por atividade. Cada pasta tem um
`enunciado.md` com o enunciado da atividade.

```
CG_26.2_8001/
├── requirements.txt              dependências compartilhadas
├── obsidian-CG_26.2_8001/        anotações interligadas (abrir no Obsidian)
├── AC1/                          Áreas da Computação Visual
│   ├── enunciado.md
│   ├── README.md
│   ├── executar_tudo.py
│   ├── relatorio/AC01_relatorio.md
│   └── 01_.. 04_..               um script por área, saída em saida/
├── AC2/                          Transformações Geométricas 2D
│   ├── enunciado.md
│   ├── transformacoes.py
│   ├── executar_ac2.py
│   ├── relatorio/AC02_relatorio.md
│   └── saida/                    10 figuras (uma por exercício)
├── AC3/                          Transformações 2D e 3D no Blender 4.5 LTS
│   ├── enunciado.md
│   ├── README.md
│   ├── AC03_parque_geometrico.py
│   └── relatorio/AC03_relatorio.md
├── AC4/                          Modelos de iluminação (Lambert, Phong, Blinn-Phong)
│   ├── enunciado.md · README.md · ac04_modelos_iluminacao.py
│   └── AC04_MichelLutegar.blend + renders
├── AC5/                          Materiais PBR e texturas (Blender 4.5)
│   ├── enunciado.md · ac05_materiais_texturas.py · validar_ac05.py
│   ├── AC05_MichelLutegar.blend  texturas empacotadas (texturas/FONTES.md)
│   └── relatorio/ · saida/
├── AP1/                          Cena-conceito 3D "Ibmec" (Blender 4.5 LTS)
│   ├── enunciado.md · README.md · ap1_ibmec_conceito.py · assets/
│   ├── relatorio/Relatorio_AP1_MichelLutegar.md  (relatório + storyboard)
│   └── saida/                    .blend + 5 imagens (Material Preview)
└── AP2/                          Animação final de 15 s (base: AC05, AP1 e AC04)
    ├── enunciado.md · README.md · ap2_ibmec_final.py · validar_ap2.py
    ├── AP2_MichelLutegar.blend · AP2_MichelLutegar.mp4
    ├── relatorio/AP2_relatorio.md · storyboard/AP2_storyboard.png
    └── saida/                    frames de apoio, curvas, prévias, teste de motor
```

## Atividades

- **AC1 — Computação Visual**: síntese, processamento, visão e visualização,
  comparadas pelo par entrada → saída. `python AC1/executar_tudo.py`.
- **AC2 — Transformações Geométricas 2D**: 10 exercícios (translação, escala,
  rotação, reflexão, cisalhamento, composições) com matrizes homogêneas e
  Matplotlib. `python AC2/transformacoes.py`.
- **AC3 — Transformações 2D e 3D no Blender 4.5 LTS**: cena "Parque Geométrico"
  com objetos 2D/3D, animação por keyframes e automação em Python. Rodar
  `AC3/AC03_parque_geometrico.py` na aba Scripting do Blender.
- **AC4 — Modelos de iluminação**: Lambert, Phong e Blinn-Phong comparados na cena da AP1.
  Ver `AC4/README.md`.
- **AC5 — Materiais PBR e texturas**: materiais Principled BSDF, UVs e mapas (cor, rugosidade,
  normal) nos objetos autorais. `blender -b --python AC5/ac05_materiais_texturas.py`;
  validar com `blender -b --python AC5/validar_ac05.py`.
- **AP1 — Cena-conceito 3D "Ibmec: Construindo o Futuro" (Blender 4.5 LTS)**:
  palavra Ibmec + 3 objetos autorais (robô, computador, foguete), câmera (não
  animada) e timeline de 360 frames @ 24 fps, em **Material Preview**. Rodar
  `blender --background --python AP1/ap1_ibmec_conceito.py` (ver `AP1/README.md`).
- **AP2 — Ibmec em 15 segundos (finalização)**: abre a cena da AC05 e entrega animação
  (câmera, palavra, objetos autorais), iluminação, render Cycles e vídeo H.264 de 15 s.
  Ver `AP2/README.md` e `AP2/relatorio/AP2_relatorio.md`.

## Blender 4.5 LTS

As atividades AC3, AC4, AC5, AP1 e AP2 usam o **Blender 4.5 LTS**. Executável no Windows:

```
C:\Program Files\Blender Foundation\Blender 4.5\blender.exe
```

Padrão de uso (PowerShell, na raiz do repositório):

```powershell
$B = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
& $B --background --python AP2\ap2_ibmec_final.py     # gerar o .blend da AP2
& $B --background --python AP2\validar_ap2.py         # validar (AP2)
& $B --background --python AC5\validar_ac05.py        # validar (AC05)
```
O render final da AP2 pede GPU NVIDIA com OptiX (Cycles) e `ffmpeg` no PATH (ver `AP2/README.md`).

## Instalação

```bash
pip install -r requirements.txt
```

Dependências: NumPy, SciPy, matplotlib, scikit-image, OpenCV e Pillow.
