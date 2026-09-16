# AC1 — Computação Visual

Material completo do Estudo Dirigido 01: relatório em Markdown e quatro
aplicações executáveis, uma para cada área da Computação Visual. Enunciado em
`enunciado.md`.

Todos os resultados citados no relatório foram gerados pelos scripts deste
pacote e a saída de console está registrada em `log_execucao.txt`.

## Execução

```bash
python AC1/executar_tudo.py
```

Executa as quatro etapas na ordem correta e grava `log_execucao.txt`.
Tempo total de referência: cerca de 36 s em uma máquina de 1 núcleo.

Para rodar uma etapa isolada (a partir de `AC1/`):

```bash
cd 01_sintese_imagens            && python raytracer.py
cd 02_processamento_imagens      && python processamento.py
cd 03_visao_computacional        && python visao.py
cd 04_visualizacao_computacional && python visualizacao.py
```

**A ordem importa.** As áreas 2 e 3 usam como entrada a imagem renderizada
pela área 1, e a área 3 compara seu resultado com o gabarito da cena 3D
salvo pela área 1. Esse encadeamento é proposital: torna verificável a
relação entre as áreas.

## Estrutura

```
AC1/
├── enunciado.md
├── executar_tudo.py             roda as 4 etapas em ordem
├── log_execucao.txt             saída de console da execução completa
├── relatorio/
│   └── AC01_relatorio.md        RELATÓRIO PRINCIPAL (entregar este)
├── 01_sintese_imagens/          cena 3D  ->  imagem  (path tracer Monte Carlo)
├── 02_processamento_imagens/    imagem  ->  imagem   (histograma, filtros, FFT)
├── 03_visao_computacional/      imagem  ->  descrição (Hough, ORB, RANSAC)
└── 04_visualizacao_computacional/  dados -> imagem   (fatias, TF, marching cubes)
```

## O que entregar

O relatório principal é `relatorio/AC01_relatorio.md`. Ele referencia todas as
figuras por caminho relativo, então basta manter a estrutura de pastas.

Para gerar um PDF a partir dele (rodando dentro de `AC1/`):

```bash
pandoc relatorio/AC01_relatorio.md -o AC01_relatorio.pdf \
  --resource-path=.:relatorio --pdf-engine=xelatex
```

Preencha o nome e a data no cabeçalho do relatório antes de entregar.

## Sobre a exigência de repositório público

A atividade pede a execução de código de repositórios públicos. O relatório
traz, em cada área, uma seção com o passo a passo do repositório correspondente:

| Área | Repositório | Seção do relatório |
|---|---|---|
| Síntese | RayTracing/raytracing.github.io | 2.4 |
| Processamento | scikit-image/scikit-image | 3.4 |
| Visão | ultralytics/ultralytics | 4.4 |
| Visualização | Slicer/Slicer (ou Kitware/ParaView) | 5.4 |

Rode pelo menos um deles, capture a tela e acrescente a imagem ao relatório.
