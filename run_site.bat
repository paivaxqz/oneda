@echo off
echo ===================================================
echo    INICIANDO PAINEL WEB (ONEDA DASHBOARD)
echo ===================================================
echo.
echo [1] Verificando dependencias...
pip install -q flask flask-login werkzeug
echo.

echo [2] Inicializando Servidor...
echo.
echo ACESSE NO NAVEGADOR: http://localhost:8080
echo (Nao feche esta janela enquanto usar o site)
echo.

python web.py
pause
