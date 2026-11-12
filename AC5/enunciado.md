# AC05 — Materiais PBR e Texturas

Ferramenta: Blender 4.5 LTS · Base: cena da [AP1](../AP1/README.md) e da [AC04](../AC4/enunciado.md)

## Contexto
Na AP1, você concebeu e modelou uma cena para apresentar a palavra Ibmec, acompanhada de três
objetos autorais. Na AC04, evoluiu essa mesma cena e comparou modelos de iluminação aplicados
aos objetos. Nesta atividade, o foco passa a ser a aparência das superfícies: você criará
materiais baseados em princípios físicos (PBR) e aplicará texturas à cena.

O resultado deve preservar o conceito e a composição das etapas anteriores. A palavra Ibmec
precisa permanecer legível e respeitar sua identidade visual; a aplicação de texturas deve se
concentrar nos outros objetos da cena.

## Objetivos
- Criar materiais com o shader Principled BSDF e compreender suas propriedades PBR.
- Preparar e avaliar coordenadas UV para posicionar texturas de imagem.
- Usar mapas de cor base, rugosidade e normal de forma adequada.
- Observar como materiais e texturas respondem à iluminação da cena.
- Organizar e documentar os materiais, mapas e fontes utilizados.

## Continuidade da AP1 e da AC04
- Abra o arquivo da AC04 e salve uma cópia como `AC05_NomeSobrenome.blend`. Não sobrescreva os arquivos da AP1 ou da AC04.
- Preserve a ideia, a composição e o enquadramento principal da cena, assim como a palavra Ibmec e os três objetos autorais.
- Use a iluminação e a câmera da AC04 como ponto de partida. Se fizer ajustes para apresentar melhor os materiais, registre-os no relatório e mantenha as condições consistentes entre as comparações.
- Crie novos materiais PBR além do objetos com os materiais usados na comparação Lambert, Phong e Blinn-Phong por materiais PBR. Os arquivos anteriores continuam preservando as etapas já realizadas.
- Atualize à palavra Ibmec com um material que mantenha suas cores e sua leitura. Não use texturas, relevos ou efeitos que comprometam sua identidade visual mas é possível uso de PBR.

## Conceitos importantes
- **Material:** conjunto de propriedades que define como uma superfície interage com a luz.
- **PBR (Physically Based Rendering):** abordagem que usa parâmetros fundamentados no comportamento dos materiais para produzir resultados coerentes sob diferentes iluminações.
- **Principled BSDF:** shader versátil do Blender que reúne propriedades como cor base, rugosidade, metalicidade, índice de refração e normal.
- **Textura:** imagem ou padrão usado para variar propriedades do material pela superfície.
- **UV:** coordenadas 2D que determinam como uma imagem é posicionada sobre a malha 3D.

Um material PBR não garante realismo sozinho: modelo, escala, UV, mapas e iluminação precisam funcionar em conjunto.

## Atividade

### 1. Preparar e organizar
- Se criar elementos auxiliares para apresentar ou testar materiais, organize-os em uma coleção chamada `AC05_Materiais_Texturas`. Mantenha os materiais nomeados de forma descritiva e preserve a organização de objetos da cena.
- Renomeie os materiais com nomes descritivos, por exemplo, `MAT_Madeira_PBR` ou `MAT_Metal_Escovado`.
- Escolha referências visuais para os materiais dos três objetos autorais. Considere o tipo de superfície, o contexto da cena e o conceito da AP1.
- Escolha texturas de imagem adequadas ao formato e à escala dos objetos. Você também pode usar texturas procedurais, desde que registre como foram criadas.

### 2. Criar materiais PBR
Crie e aplique um material ao Principled BSDF para cada um dos três objetos que pareçam com metal, madeira, espelho:
- Ajuste Base Color, Roughness e Metallic de acordo com o material escolhido.
- Use valores coerentes: metalicidade alta apenas para superfícies metálicas; materiais não metálicos geralmente usam Metallic = 0.
- Ajuste a rugosidade para controlar a nitidez dos reflexos. Compare o material sob a iluminação da cena, não apenas no Shader Editor.
- O terceiro material pode ser baseado em cor sólida, textura procedural ou imagem; os três objetos ainda devem ter materiais PBR identificáveis.

### 3. Preparar UVs e aplicar mapas
- Crie ou revise um mapa UV para cada objeto autoral que receber textura de imagem. Escolha um método de projeção adequado à forma e inspecione as ilhas no UV Editor.
- Aplique texturas de imagem a pelo menos dois dos objetos.
- Em pelo menos um material, use um conjunto que demonstre os três canais:
  - **Base Color/Albedo:** conectado ao Base Color do Principled BSDF.
  - **Roughness:** conectado ao Roughness.
  - **Normal:** conectado ao nó Normal Map, cuja saída vai ao Normal do Principled BSDF.
- No segundo objeto texturizado, use ao menos uma textura de imagem adequada e configure corretamente o material.
- Um mapa Metallic é opcional; use-o somente quando fizer sentido para o material. Não trate mapas de dados como mapas de cor.

**Espaço de cor:** imagens de cor base devem ser interpretadas como cor (normalmente sRGB). Mapas de roughness, metallic e normal contêm dados; configure-os como Non-Color. Um mapa normal tangente deve passar pelo nó Normal Map antes de chegar à entrada Normal.

### 4. Revisar a cena
- Compare os objetos no Material Preview e no Rendered, usando a câmera principal.
- Verifique escala, orientação, distorção e repetição das texturas; corrija o mapa UV ou o mapeamento quando necessário.
- Observe se a rugosidade e os relevos aparecem sob a iluminação definida.
- Faça ajustes de iluminação apenas quando necessários à leitura dos materiais e registre as mudanças.
- Confirme que a palavra Ibmec continua legível e que a composição da AP1 foi preservada.

## Requisitos
- Utilizar Blender 4.5 LTS e entregar uma cópia da cena da AC04.
- Preservar a composição da AP1/AC04, a palavra Ibmec e seus três objetos autorais.
- Aplicar materiais baseados no Principled BSDF aos três objetos autorais.
- Configurar UVs para os objetos autorais texturizados e usar texturas de imagem em pelo menos dois.
- Demonstrar os mapas Base Color, Roughness e Normal em pelo menos um dos materiais.
- Configurar corretamente o espaço de cor dos mapas de dados e a ligação do mapa normal.
- Manter a palavra Ibmec visualmente íntegra, sem texturas que prejudiquem sua leitura.
- Organizar os materiais e empacotar as imagens externas no arquivo `.blend` (File > External Data > Pack Resources) ou manter os recursos entregues junto ao projeto, sem caminhos locais quebrados.

## Entregáveis
- Arquivo `AC05_NomeSobrenome.blend`, com a cena, os materiais e as texturas configurados.
- Uma imagem renderizada pela câmera principal, apresentando a cena final.
- Uma captura do Shader Editor mostrando os nós de um material com Base Color, Roughness e Normal.
- Uma captura do UV Editor de um dos objetos texturizados.
- Relatório curto (`.md` ou `.pdf`) contendo:
  - identificação dos três objetos e descrição dos materiais aplicados;
  - propriedades principais de cada material (Base Color, Roughness, Metallic e outros pertinentes);
  - mapas utilizados e como foram conectados;
  - método de UV utilizado e ajustes feitos para reduzir distorções;
  - origem e licença das texturas externas, quando utilizadas;
  - breve observação sobre como a iluminação influenciou a aparência.

## Recursos e referências
- Introdução aos materiais no Blender
- Texturas em computação gráfica
- Introdução ao UV Unwrapping
- Texturas no Blender
- Poly Haven: texturas PBR
- ambientCG: materiais e texturas
- Blender 4.5 LTS: documentação oficial

Use texturas cuja licença permita o uso pretendido e registre sua fonte no relatório.
