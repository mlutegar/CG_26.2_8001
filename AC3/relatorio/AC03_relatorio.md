# Estudo Dirigido 03 — Transformações 2D e 3D no Blender 4.5 LTS

**Disciplina:** Computação Gráfica
**Atividade:** AC3 — Cena "Parque Geométrico" (Blender 4.5 LTS)
**Aluno(a):** Michel Lutegar
**Data:** _____________________

---

## 1. Objetivo e método

Montar a cena **"Parque Geométrico"** no Blender 4.5 LTS com objetos 2D e 3D,
aplicar transformações geométricas (translação, rotação e escala) em espaço
local e global, criar uma animação curta com keyframes e automatizar a
construção com um script Python (`AC03_parque_geometrico.py`).

Todos os objetos ficam na coleção `AC03_transformacoes`. Rotações definidas por
script usam `math.radians()` para converter graus em radianos, pois
`rotation_euler` é expresso em radianos.

Execução: abrir o Blender → aba **Scripting** → rodar `AC03_parque_geometrico.py`
→ Play na timeline → **F12** para renderizar.

---

## 2. Cena e transformações aplicadas

### Elementos 2D (plano XY)
| Objeto | Primitiva | Transformação |
|---|---|---|
| `obj2d_quadrado` | Plane | Translação X/Y + rotação Z (animado) |
| `obj2d_triangulo` | Plane editado (bmesh, 3 vértices) | Posicionamento no XY |
| `obj2d_circulo` | Mesh Circle (NGON) | Escala não uniforme X/Y `(1.5, 0.7)` |

### Elementos 3D
| Objeto | Primitiva | Transformação |
|---|---|---|
| `obj3d_cubo` | Cube | Translação X/Y/Z + rotação X/Y/Z `(25°,15°,40°)` + escala `(1.2,0.8,1.5)` |
| `obj3d_cilindro` | Cylinder | Rotação 90° em X (deitado) |
| `obj3d_esfera` | UV Sphere | Escala + rotação X/Z (animado) |

Os três eixos principais (X, Y, Z) são cobertos ao longo da cena.

### Animação (frames 1→120, 24 fps ≈ 5 s)
- **`obj2d_quadrado`** (2D): translada e rotaciona em Z, com keyframes nos
  frames 1, 60 (etapa intermediária) e 120.
- **`obj3d_esfera`** (3D): escala e rotaciona em eixos diferentes (X e Z), com
  keyframes nos frames 1 e 120.

### Bônus
- **Hierarquia parent/child:** o círculo é filho do quadrado, então mover/rotar
  o quadrado arrasta o círculo junto (transformação composta).
- **Variação temporal / easing:** keyframe intermediário no quadrado e
  interpolação `BEZIER` com `EASE_IN_OUT` na esfera.

---

## 3. Texto de entrega (manual vs. Python)

A construção da cena — criação dos seis objetos, posicionamento, transformações
iniciais, hierarquia, keyframes, câmera e luz — foi feita por **Python** na aba
Scripting, garantindo reprodutibilidade. As transformações 2D aplicadas foram
translação e rotação (quadrado) e escala não uniforme (círculo); em 3D, o cubo
recebeu translação, rotação nos três eixos e escala, e a esfera foi animada com
escala + rotação em eixos distintos. A parte **manual** consiste em ajustes
finos em Object Mode com `G` (mover), `R` (rotacionar) e `S` (escalar) sobre um
objeto, além do enquadramento da câmera e do render final (F12). Assim ficam
demonstradas as duas formas de trabalho pedidas pelo enunciado.

---

## 4. Questões teóricas

**1. Diferença entre translação, rotação e escala.**
Translação desloca o objeto somando um vetor às coordenadas (muda posição, não
forma). Rotação gira o objeto em torno de um eixo/ponto por um ângulo (muda
orientação, preserva tamanho). Escala multiplica as coordenadas por fatores
(muda tamanho/proporção); uniforme preserva a forma, não uniforme deforma.

**2. Espaço local vs. global.**
No espaço **global** a transformação usa os eixos do mundo (comuns a toda a
cena). No espaço **local** usa os eixos próprios do objeto, que acompanham sua
orientação atual. Após uma rotação, mover "para cima" em local difere de mover
"para cima" em global, pois os eixos locais já estão inclinados.

**3. Por que rotações em eixos diferentes geram resultados distintos.**
Rotações 3D não são comutativas: `Rx·Ry ≠ Ry·Rx`. Cada rotação redefine a
orientação dos eixos para a próxima, então a ordem (ex.: ângulos de Euler
X→Y→Z) altera o resultado final e pode causar efeitos como gimbal lock.

**4. Por que usar `math.radians()` em `rotation_euler`.**
A API do Blender armazena `rotation_euler` em **radianos**, mas pensamos em
graus. `math.radians(40)` converte 40° para o valor correto (~0,698 rad);
atribuir `40` diretamente giraria ~2292°.

**5. Quando usar Python em vez da interface.**
Quando a tarefa é repetitiva ou paramétrica — ex.: criar uma grade de 100 cubos
com posições/rotações calculadas, ou reaplicar a mesma cena com valores
diferentes. O script é reproduzível, versionável e evita cliques manuais.

---

## 5. Entregáveis

| Arquivo | Descrição |
|---|---|
| `AC03_NomeSobrenome.blend` | Cena salva no Blender (gerar via Save As) |
| `AC03_parque_geometrico.py` | Script Python da cena (renomear para `AC03_NomeSobrenome.py`) |
| `AC03_NomeSobrenome.png` | Render estático (F12 → Image > Save) |

> Observação: `.blend` e `.png` são gerados dentro do Blender ao executar o
> script e renderizar; não podem ser produzidos fora do Blender.
