# CG_26.2_8001 — Computação Gráfica

Repositório da disciplina. Contém duas atividades:

- **AC01 — Computação Visual** (síntese, processamento, visão, visualização).
- **AC02 — Transformações Geométricas 2D** (`AC02_transformacoes_geometricas/`):
  10 exercícios de translação, escala, rotação, reflexão, cisalhamento e
  composições, resolvidos com matrizes homogêneas e Matplotlib. Rode com
  `python AC02_transformacoes_geometricas/transformacoes.py` (ou
  `executar_ac2.py` para gravar o log). Relatório: `relatorio/AC02_relatorio.md`.

Anotações interligadas em `obsidian-CG_26.2_8001/` (abra a pasta no Obsidian).

---

# AC01 — Computação Visual

Material completo do Estudo Dirigido 01: relatório em Markdown e quatro
aplicações executáveis, uma para cada área da Computação Visual.

Todos os resultados citados no relatório foram gerados pelos scripts deste
pacote e a saída de console está registrada em `log_execucao.txt`.

## Instalação

```bash
pip install -r requirements.txt
```

Dependências: NumPy, SciPy, matplotlib, scikit-image, OpenCV e Pillow.
Não é necessária GPU. Testado com Python 3.12.

## Execução

```bash
python executar_tudo.py
```

Executa as quatro etapas na ordem correta e grava `log_execucao.txt`.
Tempo total de referência: cerca de 36 s em uma máquina de 1 núcleo.

Para rodar uma etapa isolada:

```bash
cd 01_sintese_imagens        && python raytracer.py
cd 02_processamento_imagens  && python processamento.py
cd 03_visao_computacional    && python visao.py
cd 04_visualizacao_computacional && python visualizacao.py
```

**A ordem importa.** As áreas 2 e 3 usam como entrada a imagem renderizada
pela área 1, e a área 3 compara seu resultado com o gabarito da cena 3D
salvo pela área 1. Esse encadeamento é proposital: ele torna verificável a
relação entre as áreas.

## Estrutura

```
AC01_computacao_visual/
├── README.md                    este arquivo
├── requirements.txt
├── executar_tudo.py             roda as 4 etapas em ordem
├── log_execucao.txt             saída de console da execução completa
│
├── relatorio/
│   └── AC01_relatorio.md        RELATÓRIO PRINCIPAL (entregar este)
│
├── 01_sintese_imagens/          cena 3D  ->  imagem
│   ├── raytracer.py             path tracer de Monte Carlo (NumPy)
│   └── saida/
│       ├── render_referencia.png
│       ├── render_001spp.png ... render_064spp.png
│       ├── comparacao_amostragem.png
│       ├── detalhe_aliasing.png
│       └── cena_gabarito.json   gabarito usado pela área 3
│
├── 02_processamento_imagens/    imagem  ->  imagem
│   ├── processamento.py         histograma, filtros, FFT, morfologia
│   └── saida/
│       ├── 01_histograma_equalizacao.png
│       ├── 02_ruido_e_filtros.png
│       ├── 03_convolucao_sobel.png
│       ├── 04_dominio_frequencia.png
│       ├── 05_morfologia.png
│       └── metricas.csv         PSNR e SSIM de cada filtro
│
├── 03_visao_computacional/      imagem  ->  descrição
│   ├── visao.py                 Hough, ORB, RANSAC
│   └── saida/
│       ├── 01_deteccao_hough.png
│       ├── 02_casamento_orb.png
│       ├── 03_homografia_ransac.png
│       └── descricao_da_cena.json   a saída simbólica da área
│
└── 04_visualizacao_computacional/   dados  ->  imagem
    ├── visualizacao.py          fatias, colormaps, TF, marching cubes
    └── saida/
        ├── 01_fatias_ortogonais.png
        ├── 02_mapas_de_cores.png
        ├── 03_funcoes_de_transferencia.png
        └── 04_isosuperficies.png
```

## O que entregar

O relatório principal é `relatorio/AC01_relatorio.md`. Ele já referencia
todas as figuras por caminho relativo, então basta manter a estrutura de
pastas ao abrir ou converter o arquivo.

Para gerar um PDF a partir dele:

```bash
pandoc relatorio/AC01_relatorio.md -o AC01_relatorio.pdf \
  --resource-path=.:relatorio --pdf-engine=xelatex
```

Preencha o nome e a data no cabeçalho do relatório antes de entregar.

## Sobre a exigência de repositório público

A atividade pede a execução de aplicação ou código de repositórios
públicos. As implementações deste pacote servem para explicar os conceitos
com números próprios, mas o relatório traz, em cada área, uma seção com o
passo a passo do repositório público correspondente:

| Área | Repositório | Seção do relatório |
|---|---|---|
| Síntese | RayTracing/raytracing.github.io | 2.4 |
| Processamento | scikit-image/scikit-image | 3.4 |
| Visão | ultralytics/ultralytics | 4.4 |
| Visualização | Slicer/Slicer (ou Kitware/ParaView) | 5.4 |

Rode pelo menos um deles, capture a tela e acrescente a imagem ao
relatório na seção correspondente.
