# AC04 — Modelos de iluminação: Lambert, Phong e Blinn-Phong

Ferramenta: Blender 4.5 LTS · Base: cena da [AP1](../AP1/README.md)

## Objetivo
Aplicar e comparar materiais inspirados nos modelos Lambert, Phong e Blinn-Phong em uma
cena 3D, observando as componentes difusa e especular e a influência da luz, da
rugosidade e do ângulo de observação.

## Continuidade da AP1
- Salvar cópia como `AC04_NomeSobrenome.blend`, sem sobrescrever o original.
- Preservar ideia, composição e leitura da palavra Ibmec e os três objetos autorais.
- Organizar materiais e luzes em coleções, com nomes claros.
- Não alterar a identidade visual da palavra; comparar nos objetos autorais.

## Atividade
1. **Iluminação:** luz principal (Area ou Sun) com sombras perceptíveis; posição, intensidade,
   cor e câmera iguais durante as comparações; preenchimento suave opcional.
2. **Materiais:** `MAT_Lambert`, `MAT_Phong`, `MAT_BlinnPhong`, um por objeto autoral, cores-base distintas.
   - Lambert: difuso, fosco (rugosidade ~1.0, especular reduzido; ou Diffuse BSDF).
   - Phong: rugosidade ~0.2, especular moderado.
   - Blinn-Phong: rugosidade ~0.1, especular mais intenso.
   - Se houver *IOR Level* em vez de *Specular*, registrar os valores usados.
3. **Comparar:** modo Rendered, ao menos um render de teste; comparar brilho, área do
   highlight, fosco × polido; girar a luz temporariamente e restaurar para a imagem final.

Nota técnica: o Principled BSDF é físico; Phong/Blinn-Phong aqui são aproximações visuais.

## Entregáveis
- `AC04_NomeSobrenome.blend`
- Render final (Ibmec legível + 3 objetos visíveis)
- Imagem de comparação dos três objetos sob a mesma luz
- Relatório curto (.md/.pdf): objetos×materiais, luzes, valores (cor, rugosidade, especular),
  comparação e explicação das aproximações

## Critérios
Continuidade e composição · aplicação dos três materiais · configuração de iluminação ·
comparação e análise · organização e entregáveis.

## Resolução neste repositório
Ver [README](README.md) e [relatório](relatorio/AC04_relatorio.md).
