@echo off
cd /d C:\Users\playk\OneDrive\Рабочий стол\3d\pifuhd
call venv_pifuhd\Scriptsctivate.bat
python -m apps.simple_test --input_path sample_images --out_path results -r 256
echo.
echo ========================================
echo ГОТОВО! Нажмите любую клавишу для выхода...
pause > nul
