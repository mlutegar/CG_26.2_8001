# Questões Teóricas

⬅️ [[AC03]] · [[Painel]]

1. **Translação / rotação / escala** — mudam, respectivamente, posição
   (soma vetor), orientação (gira em torno de eixo) e tamanho (multiplica
   coordenadas). Escala uniforme preserva forma; não uniforme deforma.
2. **Local vs. global** — local usa os eixos próprios do objeto (que giram com
   ele); global usa os eixos do mundo. Após rotacionar, os resultados divergem.
3. **Rotações em eixos diferentes** — não são comutativas (`Rx·Ry ≠ Ry·Rx`); a
   ordem muda o resultado e pode causar gimbal lock.
4. **`math.radians()`** — `rotation_euler` é em radianos; converter evita
   girar o valor errado (ex.: 40 rad em vez de 40°).
5. **Python vs. interface** — vale a pena em tarefas repetitivas/paramétricas
   (ex.: gerar uma grade de 100 objetos calculados), por ser reproduzível.

Respostas completas em `AC3/relatorio/AC03_relatorio.md`.
