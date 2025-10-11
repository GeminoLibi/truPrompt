@echo off
echo ========================================
echo dataPull Agent Prompt Generator
echo Python Version (Alternative)
echo ========================================
echo.
echo This runs the Python version directly.
echo Make sure Python is installed on your system.
echo.
pause
echo.
cd data
python run_prompt_generator.py
echo.
echo ========================================
echo Generation complete!
echo ========================================
echo.
echo Check the 'outputs' folder for your generated prompts.
echo.
pause
