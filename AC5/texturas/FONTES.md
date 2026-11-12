# Fontes das texturas (AC05)

Todas as texturas são CC0 (domínio público), de uso livre, inclusive acadêmico, sem exigência de atribuição.
Resolução usada: 1K (1024 x 1024), formato JPG.

| Textura | Fonte | URL | Autor | Licença | Uso na cena |
|---|---|---|---|---|---|
| Brown Planks 03 (`brown_planks_03`) | Poly Haven | https://polyhaven.com/a/brown_planks_03 | Rob Tuytel | CC0 | MAT_Madeira_PBR (computador): Base Color, Roughness, Normal |
| Metal 009 (`Metal009`) | ambientCG | https://ambientcg.com/a/Metal009 | ambientCG | CC0 | MAT_Metal_Escovado_PBR (foguete): Base Color, Roughness, Normal |

## Arquivos

Poly Haven (`wood/`), baixados de `https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/brown_planks_03/`:
- `brown_planks_03_diff_1k.jpg` (cor, sRGB)
- `brown_planks_03_rough_1k.jpg` (rugosidade, Non-Color)
- `brown_planks_03_nor_gl_1k.jpg` (normal OpenGL, Non-Color)

ambientCG (`Metal009/`), baixados de `https://ambientcg.com/get?file=Metal009_1K-JPG.zip`:
- `Metal009_1K-JPG_Color.jpg` (cor, sRGB)
- `Metal009_1K-JPG_Roughness.jpg` (rugosidade, Non-Color)
- `Metal009_1K-JPG_NormalGL.jpg` (normal OpenGL, Non-Color)
- `Metal009.png` (pré-visualização do site)

Os mapas normais estão no formato OpenGL (Y+), o esperado pelo nó Normal Map do Blender.
Os demais mapas do pacote (Displacement, NormalDX, Metalness) foram descartados por não serem usados.

## HDRI (reflexos do robô)

| Item | Dado |
|---|---|
| HDRI | Studio Small 08 (`studio_small_08`), 1K, formato `.hdr` |
| Fonte | Poly Haven, https://polyhaven.com/a/studio_small_08 |
| Autor | Sergej Majboroda |
| Licença | CC0 (domínio público) |
| Arquivo | `hdri/studio_small_08_1k.hdr`, baixado de `https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/studio_small_08_1k.hdr` |
| Uso | World, somente para raios glossy (Light Path > Is Glossy Ray). Empacotado no `.blend` como `hdri_studio_small_08`. |
