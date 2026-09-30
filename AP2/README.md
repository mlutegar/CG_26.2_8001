# AP2 — Peça final animada "Ibmec: Construindo o Futuro"

Evolução da cena-conceito da **AP1** para a peça final: animação, iluminação,
materiais/texturas, composição/acabamento e render/exportação do vídeo.

A AP2 **reutiliza a cena da AP1**: o script importa os construtores de
`../AP1/ap1_ibmec_conceito.py` e os assets de `../AP1/assets/`, e então aplica
todo o acabamento e a animação.

## Conteúdo
```
AP2/
├── enunciado.md              o que a AP2 desenvolve
├── README.md
├── ap2_ibmec_final.py        cena da AP1 + acabamento + animação + render
├── _render_capas.py          gera as imagens-capa (HD/Cycles/vertical)
├── relatorio/AP2_relatorio.md
└── saida/
    ├── AP2_MichelLutegar.blend
    ├── AP2_animacao.mp4       peça final (15 s, 24 fps, H.264)
    ├── cena_capa_cycles.png   capa Cycles 1080p
    ├── cena_hd.png            Eevee 1080p
    └── cena_capa_vertical.png 9:16
```

## Como gerar
```powershell
# 1) animação + .blend final (AP2/saida)
$env:AP2_ANIMAR = "1"
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background --python AP2\ap2_ibmec_final.py

# 2) imagens-capa
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  -b AP2\saida\AP2_MichelLutegar.blend --python AP2\_render_capas.py
```
(Com `AP2_ANIMAR=0` gera só os stills + `.blend`, sem o vídeo.)

## O que a AP2 desenvolve (sobre a base da AP1)
- **Animação por keyframes**: blocos se assentam → palavra sobe + pingo encaixa
  (com pulso) → foguete decola (chama + fumaça); câmera com *push-in*.
- **Iluminação**: sol (chave) + área (preenchimento) + rim light azul.
- **Materiais/texturas**: cores da marca, verniz na palavra, textura procedural
  no chão (Noise + Bump), planeta ao fundo.
- **Composição/acabamento**: profundidade de campo, bloom, vinheta e color
  grading (Compositor); fundo espacial (gradiente + estrelas + nebulosa).
- **Render/exportação**: Eevee para o vídeo (H.264) e Cycles para a capa.

A ideia central e a organização (coleção `AP1_Ibmec_Conceito`, nomes dos
objetos) são preservadas da AP1.
