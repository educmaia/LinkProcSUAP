@echo off
echo ============================================================
echo           WEB SCRAPER SUAP - COLETA DE LINKS
echo ============================================================
echo.
echo IMPORTANTE: O navegador abrira automaticamente
echo Voce devera fazer login no SUAP manualmente
echo Apos o login, volte a este terminal e pressione ENTER
echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo Executando scraper...
python web_scraper_suap.py
echo.
echo Processamento concluido!
pause