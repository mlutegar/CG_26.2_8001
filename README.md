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
├── AP1/                          Cena-conceito 3D "Ibmec" (Blender 4.5 LTS)
│   ├── enunciado.md · README.md · ap1_ibmec_conceito.py · assets/
│   ├── relatorio/Relatorio_AP1_MichelLutegar.md  (relatório + storyboard)
│   └── saida/                    .blend + 4 imagens viewport (Workbench)
└── AP2/                          Peça final animada (evolução da AP1)
    ├── enunciado.md · README.md · ap2_ibmec_final.py · _render_capas.py
    ├── relatorio/AP2_relatorio.md
    └── saida/                    .blend + AP2_animacao.mp4 + capas
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
- **AP1 — Cena-conceito 3D "Ibmec: Construindo o Futuro" (Blender 4.5 LTS)**:
  palavra Ibmec + 3 objetos autorais (robô, computador, foguete), câmera (não
  animada) e timeline de 360 frames @ 24 fps, em **Workbench solid**. Rodar
  `blender --background --python AP1/ap1_ibmec_conceito.py` (ver `AP1/README.md`).
- **AP2 — Peça final animada (evolução da AP1)**: importa a cena da AP1 e adiciona
  animação, iluminação, materiais/texturas, acabamento e render do vídeo
  (`AP2_animacao.mp4`). Rodar `blender --background --python AP2/ap2_ibmec_final.py`
  (ver `AP2/README.md`).

## Instalação

```bash
pip install -r requirements.txt
```

Dependências: NumPy, SciPy, matplotlib, scikit-image, OpenCV e Pillow.
