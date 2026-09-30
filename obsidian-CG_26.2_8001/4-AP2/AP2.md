# AP2 — Peça final animada

⬅️ [[Painel]] · base: [[AP1]]

Evolução da cena-conceito da AP1 para a **peça final de ~15 s**. O script
`AP2/ap2_ibmec_final.py` **importa** a cena da AP1 e aplica o acabamento.

## Enquadramento (acabamento)
![[enquadramento_principal.png]]

## O que a AP2 desenvolve
- **Animação** por keyframes: blocos → palavra sobe + pingo encaixa (pulso) →
  foguete decola (chama + fumaça); câmera com *push-in*.
- **Iluminação**: sol + preenchimento + rim light azul.
- **Materiais/texturas**: cores da marca, verniz na palavra, textura no chão.
- **Composição/acabamento**: DoF, bloom, vinheta, color grading; fundo espacial
  (gradiente + estrelas + nebulosa + planeta).
- **Render/exportação**: Eevee (vídeo `AP2_animacao.mp4`) + Cycles (capa).

## Entregáveis
`AP2/saida/`: `AP2_MichelLutegar.blend`, `AP2_animacao.mp4`,
`cena_capa_cycles.png`, `cena_hd.png`, `cena_capa_vertical.png`.

Relatório: `AP2/relatorio/AP2_relatorio.md` · Enunciado: `AP2/enunciado.md`.

A ideia central e a organização vêm de [[AP1]] (preservadas). Ver [[Plano-AP2]].
