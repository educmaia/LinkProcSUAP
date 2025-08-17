@echo off
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
echo.
echo Ambiente virtual ativado!
echo Para executar o scraper: python web_scraper_suap.py
echo Para executar exemplos: python exemplo_uso.py
echo Para desativar: deactivate
echo.
cmd /k