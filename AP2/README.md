# AP2: Ibmec em 15 segundos (finalização)

Peça animada de 15 s (360 frames, 24 fps, 1920x1080, H.264), feita no **Blender 4.5 LTS** (Cycles OptiX, 64 spp, motion blur 0,35).
Parte da cena da **AC05** (materiais PBR e UVs), com o conceito e o storyboard da **AP1** e a iluminação estudada na **AC04**.
O script abre `AC5/AC05_MichelLutegar.blend` somente para leitura e salva `AP2/AP2_MichelLutegar.blend`.

Relatório: [relatorio/AP2_relatorio.md](relatorio/AP2_relatorio.md) · Storyboard: [storyboard/AP2_storyboard.png](storyboard/AP2_storyboard.png)

## Conteúdo
```
AP2/
├── enunciado.md · README.md
├── AP2_MichelLutegar.blend        cena final (imagens empacotadas)
├── AP2_MichelLutegar.mp4          vídeo final (H.264, 15 s)
├── ap2_ibmec_final.py             gera o .blend, prévias, testes e render
├── validar_ap2.py                 validação automática (65 verificações)
├── gerar_curvas.py                curvas e tabela de animação
├── gerar_storyboard.py            storyboard e comparação de motor
├── relatorio/AP2_relatorio.md
├── storyboard/AP2_storyboard.png
├── _versao_antiga/                AP2 anterior (objetos da AP1 antiga)
└── saida/                         imagens, curvas, prévias, teste de motor
                                   (frames/, teste_rapido/ e _tmp/ ficam fora do Git)
```

## Como rodar (Windows, PowerShell, a partir da raiz do repositório)
```powershell
$B = "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"

# 1) gerar o .blend (abre a AC05, organiza a cena e cria as animações)
& $B --background --python AP2\ap2_ibmec_final.py

# 2) render de teste: 7 prévias 960x540 em saida\previas
$env:AP2_RENDER_TESTE = "1"; & $B -b --python AP2\ap2_ibmec_final.py; Remove-Item Env:AP2_RENDER_TESTE
#    teste rápido da sequência inteira (960x540, 16 spp) em saida\teste_rapido
$env:AP2_RENDER_RAPIDO = "1"; & $B -b --python AP2\ap2_ibmec_final.py; Remove-Item Env:AP2_RENDER_RAPIDO

# 3) render final: 360 PNG 1920x1080, Cycles OptiX 64 spp (~33 min na RTX 3050) em saida\frames
$env:AP2_RENDER_SEQ_FINAL = "1"; & $B -b --python AP2\ap2_ibmec_final.py; Remove-Item Env:AP2_RENDER_SEQ_FINAL
#    montar o MP4 H.264 (ffmpeg no PATH)
ffmpeg -framerate 24 -i AP2\saida\frames\f_%04d.png -c:v libx264 -crf 14 -pix_fmt yuv420p AP2\AP2_MichelLutegar.mp4

# 4) validar o .blend e conferir o vídeo
& $B -b --python AP2\validar_ap2.py
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration -of default=nw=1 AP2\AP2_MichelLutegar.mp4
```
Atenção: os passos 1 a 3 regravam o `.blend` e o `.mp4` entregues. `AP2_RENDER_FINAL=1` é o caminho alternativo
(o Blender grava o MP4 direto, sem PNG). Outros: `AP2_RENDER_MOTOR=1` (teste Eevee x Cycles),
`AP2_RENDER_TEXTURAS=1` (recortes de textura em movimento), `AP2_MOTOR=EEVEE`, `AP2_FRAMES=a-b`, `AP2_ESCALA`, `AP2_DESTINO`.
Curvas: `python AP2\gerar_curvas.py` (no Blender). Storyboard e comparação de motor: `python AP2\gerar_storyboard.py`
(precisa de `saida\frames\`).

## O que a AP2 entrega
- **Animação**: câmera (push-in 1 a 330, travada até 360), palavra Ibmec, ponto do i, 5 blocos, robô (cabeça e braço), tela do computador e foguete com chama.
- **Iluminação**: Sun + Area, fundo cinza e HDRI só em raios glossy; rim testado e descartado; emissões limitadas.
- **Materiais**: PBR da AC05 (robô, madeira, metal, marca); tela e chama novas.
- **Render**: Cycles OptiX 64 spp, motion blur 0,35; vídeo H.264 conferido com ffprobe.
- Principled BSDF é um modelo baseado em física, não é Phong nem Blinn-Phong.

Texturas e HDRI: CC0 (Poly Haven e ambientCG), ver `AC5/texturas/FONTES.md`.

## Modo apresentação
Abre o `.blend` já arrumado para mostrar a AP2 ao vivo, sem alterar o arquivo.

**Como abrir**
- Duplo clique em `AP2presentar.bat` (usa `C:\Program Files\Blender Foundation\Blender 4.5lender.exe`; se não existir, procura `blender.exe` no PATH e avisa se não achar), ou
- `blender.exe AP2\AP2_MichelLutegar.blend --python AP2presentacao_ap2.py`

O script nunca salva o `.blend`, desliga o autosave e não grava as preferências. Tudo vale só para a sessão.
Ele começa no workspace **Animation** e, se você trocar de workspace, arruma a nova tela sozinho (volta ao Object Mode quando preciso).

**O que cada workspace mostra**
- **Animation**: vista da câmera em Material Preview com overlays mínimos, frame 1, marcadores (Inicio, Desenvolvimento, Encerramento) visíveis na timeline e Graph Editor com `Palavra_Ibmec` e `Cam_Principal` selecionados e as curvas enquadradas.
- **Shading**: `Obj_Computador_Corpo` ativo e o `MAT_Madeira_PBR` no Shader Editor (em tela cheia, Ctrl+Espaço volta), com todos os nós enquadrados e legíveis.
- **UV Editing**: `Obj_Computador_Corpo` em Edit Mode com todas as faces selecionadas e a imagem de cor da madeira no Image Editor, com as ilhas enquadradas.

**Cycles e o F12**
O script detecta GPU OptiX ou CUDA e mostra no console qual dispositivo está em uso. Sem GPU, usa CPU, reduz o F12 para 16 amostras com denoise (OpenImageDenoise) só nesta sessão, e avisa no console.
Para simular um PC sem GPU: `set AP2_FORCAR_CPU=1` antes de abrir. Medido no frame 360 (1920x1080): GPU OptiX com 64 amostras em 7,7 s; CPU com 16 amostras e denoise em 25,2 s.

