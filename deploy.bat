@echo off
cd /d "%~dp0"
git add .
git commit -m "Mise a jour %date%"
git push
pause
