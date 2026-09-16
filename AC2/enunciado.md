# AC2 — Enunciado

**Disciplina:** Computação Gráfica
**Atividade:** AC2 — Transformações geométricas 2D com Matplotlib

## Objetivo

Plotar exercícios de transformações geométricas usando Matplotlib, definindo
uma forma, aplicando a transformação e plotando o objeto antes e depois.

## Exercícios

1. **Translação simples** — `P(2, 3)`, vetor `(4, −2)`. Qual é `P'`? Quais
   coordenadas mudaram?
2. **Escala uniforme** — triângulo `A(1,1) B(3,1) C(2,4)`, fator 2. Novas
   coordenadas? O que acontece com o tamanho?
3. **Escala não uniforme** — triângulo do Ex2, fator 2 em x e 0,5 em y.
4. **Rotação em torno da origem** — `P(1,0)`, 90° anti-horário.
5. **Rotação de um polígono** — quadrado `A(1,1) B(1,4) C(4,4) D(4,1)`, 45°
   horário.
6. **Reflexão simples** — `P(2,5)`, reflexão no eixo y.
7. **Reflexão de um triângulo** — `A(2,3) B(4,3) C(3,5)`, reflexão no eixo x.
8. **Cisalhamento horizontal** — `P(2,3)`, `k = 2`.
9. **Composição de transformações** — `P(3,2)`: translação `(1,−1)`, depois
   rotação 90° anti-horário, depois escala uniforme 2.
10. **Combinação em uma figura** — retângulo `A(1,1) B(5,1) C(5,3) D(1,3)`:
    translação `(−2,3)`, escala não uniforme `(1.5, 0.5)`, reflexão no eixo y.

## Como executar

```bash
pip install -r requirements.txt
python AC2/transformacoes.py      # imprime respostas e gera 10 figuras em saida/
python AC2/executar_ac2.py        # idem, gravando log_ac2.txt
```

Relatório: `AC2/relatorio/AC02_relatorio.md`.
