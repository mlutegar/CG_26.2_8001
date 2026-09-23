# AC3 — Transformações Geométricas 2D e 3D no Blender 4.5 LTS

Cena **"Parque Geométrico"**: objetos 2D (quadrado, triângulo, círculo) e 3D
(cubo, cilindro, esfera UV) com transformações, animação por keyframes e
automação em Python.

## Estrutura
```
AC3/
├── enunciado.md                    enunciado da atividade
├── AC03_parque_geometrico.py       script para a aba Scripting do Blender
└── relatorio/AC03_relatorio.md     relatório + respostas teóricas
```

## Como executar
1. Abra o **Blender 4.5 LTS**.
2. Vá à aba **Scripting**.
3. Abra `AC03_parque_geometrico.py` (Text > Open) e ajuste a variável `ALUNO`.
4. Clique em **Run Script** (▶) ou `Alt+P`. A coleção `AC03_transformacoes` é
   criada com os 6 objetos, animação, câmera e luz.
5. Dê **Play** na timeline (frames 1→120, 24 fps) para ver a animação.
6. Pressione **F12** para renderizar; salve como `AC03_NomeSobrenome.png`.
7. Faça um ajuste **manual** com `G`/`R`/`S` (exigido pelo enunciado) e salve o
   arquivo como `AC03_NomeSobrenome.blend`.

## Entregáveis
- `AC03_NomeSobrenome.blend`
- `AC03_NomeSobrenome.py` (este script renomeado)
- `AC03_NomeSobrenome.png`
- Texto curto de entrega — ver `relatorio/AC03_relatorio.md`.

> `.blend` e `.png` só podem ser gerados dentro do Blender.
