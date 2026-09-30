# AP1 — Cena-conceito "Ibmec: Construindo o Futuro" (Blender 4.5 LTS)

Base visual e geométrica da peça audiovisual (a animação/render fica para a AP2).
A cena é construída **programaticamente** por um script `bpy`, o que garante
reprodutibilidade e organização (coleções e nomes coerentes).

## Conteúdo
```
AP1/
├── enunciado.md                         enunciado da atividade
├── ap1_ibmec_conceito.py                script que constroi a cena inteira
├── assets/                              logo + fontes (usados pela palavra)
├── relatorio/
│   └── Relatorio_AP1_MichelLutegar.md   relatório + storyboard (template oficial)
└── saida/                               gerada ao executar
    ├── AP1_MichelLutegar.blend
    ├── enquadramento_principal.png
    └── obj_robo.png / obj_computador.png / obj_foguete.png
```

## Como gerar os entregáveis

**1. Edite o autor.** Abra `ap1_ibmec_conceito.py` e troque a constante do topo:
```python
AUTOR = "NomeSobrenome"   # -> ex.: "JoaoSilva"
```

**2a. Modo gráfico (recomendado para ajustar a gosto):**
abra o Blender 4.5 → aba **Scripting** → **Open** `ap1_ibmec_conceito.py` →
**Run Script**. A cena aparece montada; salve/renderize como quiser.

**2b. Modo headless (gera .blend + as 4 imagens de uma vez):**
```powershell
& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
  --background --python AP1\ap1_ibmec_conceito.py
```
Saída em `AP1/saida/`. As imagens também são copiadas para o vault Obsidian
(`obsidian-CG_26.2_8001/3-AP1/img/`) se ele existir.

## O que o script cria (cena-conceito)
- Coleção **AP1_Ibmec_Conceito** (subcoleções Palavra / Objetos / Auxiliares).
- **Palavra_Ibmec** (texto Krub → malha, extrusão + bevel) + ponto laranja do
  "i"; azul-marinho, legível e em destaque.
- **3 objetos autorais:** `Obj_Robo`, `Obj_Computador`, `Obj_Foguete` (nomes coerentes).
- Auxiliares: `Aux_Chao` + `Aux_Bloco_01..05` (a "construção" da marca).
- **Cam_Principal** com *Track To* mirando a palavra — **não animada**, pronta p/ AP2.
- Timeline **360 frames @ 24 fps** + 3 marcadores de storyboard.
- Apresentação em **Material Preview** (Eevee + materiais simples das cores +
  mundo/sol de preview): enquadramento principal, 3 closes dos objetos e uma
  **vista geral** (ângulo alternativo) + salvamento do `.blend`.

> Materiais, iluminação, animação, composição/acabamento e render final **não**
> fazem parte da AP1 — ficam para a **AP2** (ver a pasta `../AP2/`).

## Técnicas de modelagem usadas (além de escalar primitivas)
extrusão, bevel, loop cut (subdivisão), inset com recuo, Array, composição de
malhas (join), curvas/texto — bem acima do mínimo de dois recursos exigido.
Distribuídas entre a palavra e os 3 objetos (ex.: robô por composição de malhas
+ inset + bevel; computador com inset da tela + loop cuts do teclado + join;
foguete com inset + join).
