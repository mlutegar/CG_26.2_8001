# AC1 — Enunciado

**Disciplina:** Computação Gráfica
**Atividade:** AC1 — Diferenças e características das áreas da Computação Visual

## Objetivo

Demonstrar, com aplicações executáveis, as diferenças entre as quatro áreas da
Computação Visual, usando como critério o par **entrada → saída** de cada área:

| Área | Entrada | Saída | Pergunta que responde |
|---|---|---|---|
| Síntese de imagens | descrição de cena 3D | imagem | "Como esta cena apareceria numa câmera?" |
| Processamento de imagens | imagem | imagem / medida | "Como melhorar/transformar esta imagem?" |
| Visão computacional | imagem | descrição simbólica | "O que existe nesta imagem?" |
| Visualização computacional | dados abstratos | imagem | "Que forma dar a dados sem forma?" |

Cada área é implementada em uma subpasta (`01_` a `04_`), com um script próprio
que gera as figuras em `saida/`. As áreas são encadeadas: 2 e 3 usam como
entrada o render da área 1.

## Como executar

```bash
python AC1/executar_tudo.py     # roda as 4 etapas e grava log_execucao.txt
```

Relatório final: `AC1/relatorio/AC01_relatorio.md`.
