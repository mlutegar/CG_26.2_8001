# AC3 — Enunciado

**Disciplina:** Computação Gráfica
**Atividade:** Transformações Geométricas 2D e 3D no Blender 4.5 LTS

## Contexto
Construir uma cena simples no Blender 4.5 LTS para praticar transformações
geométricas em nível introdutório, combinando manipulação manual (interface) e
automação básica com Python.

## Objetivos de aprendizagem
- Aplicar transformações 2D em objetos planos (translação, rotação e escala).
- Aplicar transformações 3D em sólidos (translação, rotação e escala em eixos distintos).
- Distinguir transformações em espaço local e espaço global.
- Criar uma animação curta com keyframes de transformações.
- Escrever um script Python simples para criar objetos e aplicar transformações.

## Ferramentas obrigatórias
- Blender 4.5 LTS.
- Janela Scripting do Blender (Python integrado).

## Enunciado da prática
Montar uma mini-cena chamada **"Parque Geométrico"** contendo:

**Elementos 2D (plano XY):**
- 1 quadrado (Plane).
- 1 triângulo (Plane editado para 3 vértices).
- 1 círculo (Mesh Circle).

**Elementos 3D:**
- 1 cubo.
- 1 cilindro.
- 1 esfera UV.

**Animação curta (3 a 6 segundos):**
- Um objeto 2D deve transladar e rotacionar.
- Um objeto 3D deve escalar e rotacionar em eixos diferentes.

**Automação com Python (obrigatória):**
- Criar ao menos 2 objetos por script.
- Aplicar pelo menos 3 transformações via script (ex.: `location`, `rotation_euler`, `scale`).

## Requisitos técnicos mínimos
- Cena organizada com nomes coerentes (ex.: `obj2d_quadrado`, `obj3d_cubo`).
- Pelo menos um caso de rotação em graus convertidos para radianos no Python.
- Ao menos uma transformação em cada eixo principal (X, Y, Z) ao longo da atividade.
- Keyframes pelo menos nos frames inicial e final para dois objetos.

## Entregáveis
- Arquivo Blender: `AC03_NomeSobrenome.blend`.
- Script Python: `AC03_NomeSobrenome.py`.
- Imagem renderizada da cena final: `AC03_NomeSobrenome.png`.
- Texto curto (5 a 10 linhas) explicando quais transformações 2D e 3D foram
  aplicadas e qual parte foi manual e qual por Python.

## Bônus (até +1,0)
- Uso de hierarquia (parent/child) para transformação composta.
- Pequena variação temporal adicional na animação (ex.: easing ou etapa intermediária).

## Questões teóricas
1. Diferença entre translação, rotação e escala em computação gráfica.
2. Diferença entre transformar um objeto no espaço local e no espaço global.
3. Por que rotações em eixos diferentes podem gerar resultados visuais distintos.
4. Por que usar `math.radians()` ao definir `rotation_euler` por script.
5. Exemplo prático de quando vale mais a pena usar Python que a interface.

## Critérios de avaliação (10,0 pontos)
- Modelagem básica da cena (2,0).
- Transformações 2D (2,0).
- Transformações 3D (2,0).
- Python introdutório (2,0).
- Animação e apresentação (2,0).
