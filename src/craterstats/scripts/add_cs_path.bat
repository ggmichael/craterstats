@echo off
set dir0=%~dp0
set "cs_dir=%dir0:~0,-1%" :: Strip trailing backslash
for %%F in ("%cs_dir%..") do set "cs_dir=%%~dpF" :: Get parent directory
set PATH=%PATH%;%cs_dir%

