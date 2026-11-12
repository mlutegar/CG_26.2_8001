# AP2 — Relatório

**Disciplina:** Computação Gráfica
**Atividade:** AP2 — Peça final animada (evolução da AP1)
**Aluno(a):** Michel Lutegar
**Data:** 30/09/2026

---

## 1. Base: a cena da AP1
A AP2 parte da **cena-conceito da AP1** (`AP1_Ibmec_Conceito`: palavra Ibmec,
livro, torre, foguete, auxiliares, câmera e timeline de 360 frames @ 24 fps). O
script `ap2_ibmec_final.py` importa os construtores da AP1 e aplica o acabamento.

## 2. Animação (keyframes + interpolação)
- **Blocos**: caem e se assentam (0–4,5 s), escalonados.
- **Palavra Ibmec**: sobe + *scale-in*; **pingo laranja** cai e encaixa no "i"
  com *overshoot* e **flash** de emissão; **pulso** ao completar (~8,3 s).
- **Foguete**: decola (sobe acelerando + giro) com **chama** e **fumaça**
  (11,7–15 s).
- **Câmera**: *push-in* suave (0–15 s), mira mantida por *Track To*.

## 3. Iluminação
Sol (luz-chave), área (preenchimento) e **rim light** azul (contorno) para
separar os objetos do fundo espacial.

## 4. Materiais e texturas
Cores da marca (azul-marinho + laranja), **verniz** (coat) na palavra, **textura
procedural** no chão (Noise → cor + Bump → relevo, com rugosidade variável),
material do planeta.

## 5. Composição e acabamento
**Profundidade de campo** (foco na palavra), **bloom**, **vinheta** e **color
grading** (Compositor). **Fundo espacial**: gradiente + duas camadas de estrelas
+ nebulosa colorida + **planeta** distante.

## 6. Renderização e exportação
- **Vídeo**: Eevee, 1280×720, 24 fps, H.264 → `saida/AP2_animacao.mp4` (15 s).
- **Capas**: Cycles 1080p (`cena_capa_cycles.png`), Eevee 1080p (`cena_hd.png`)
  e vertical 9:16 (`cena_capa_vertical.png`).

## 7. Preservação da AP1
A ideia central (construção/lançamento da marca) e a organização (coleção,
nomes dos objetos, câmera) foram preservadas; a modelagem foi refinada
(antena, bocal, livro em camadas) sem mudar o conceito.

---
Reprodução: ver `AP2/README.md`.
