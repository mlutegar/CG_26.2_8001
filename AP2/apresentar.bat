@echo off
rem AP2: abre o Blender 4.5 em modo apresentacao (nao salva o .blend).
setlocal
set "BLENDER=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
if not exist "%BLENDER%" (
    set "BLENDER="
    for /f "delims=" %%I in ('where blender.exe 2^>nul') do if not defined BLENDER set "BLENDER=%%I"
)
if not defined BLENDER (
    echo [AP2] AVISO: blender.exe nao encontrado.
    echo Instale o Blender 4.5 em "C:\Program Files\Blender Foundation\Blender 4.5" ou coloque blender.exe no PATH.
    pause
    exit /b 1
)
echo [AP2] Usando: %BLENDER%
"%BLENDER%" "%~dp0AP2_MichelLutegar.blend" --python "%~dp0apresentacao_ap2.py"
endlocal
