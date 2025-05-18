@echo off
set "SRC_EXE=storm_watcher.exe"
set "TARGET_DIR=%APPDATA%\StormWatcher"
set "TARGET_EXE=%TARGET_DIR%\storm_watcher.exe"

echo Установка PhpStormWatcher...

:: Создание папки
mkdir "%TARGET_DIR%" >nul 2>&1

:: Копирование exe
copy /Y "%~dp0%SRC_EXE%" "%TARGET_DIR%" >nul

:: Добавление в автозапуск
reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v PhpStormWatcher /d "%TARGET_EXE%" /f

:: Запуск
start "" "%TARGET_EXE%"

echo Установка завершена. Нажмите любую клавишу...
pause >nul
