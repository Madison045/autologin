@echo off
echo ========================================
echo AutoLogin - Сборка EXE
echo ========================================

REM Установка зависимостей
echo Устанавливаю зависимости...
pip install selenium webdriver-manager pyinstaller

REM Сборка EXE
echo Собираю EXE файл...
pyinstaller --onefile ^
            --windowed ^
            --name=AutoLogin ^
            --icon=icon.ico ^
            --add-data="autologin_config.json;." ^
            autologin.py

echo.
echo ========================================
echo СБОРКА ЗАВЕРШЕНА!
echo.
echo EXE файл: dist\AutoLogin.exe
echo ========================================
pause