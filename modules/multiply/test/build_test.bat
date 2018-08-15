@echo off

set MODULE_PATH=%~dp0\..
set FRAMEWORK_PATH=%~dp0\..\..\framework

gcc %FRAMEWORK_PATH%\Unity\src\unity.c %MODULE_PATH%\multiply.c %MODULE_PATH%\test\Testmultiply.c %MODULE_PATH%\test\Testmultiply_Runner.c -I%MODULE_PATH% -I%FRAMEWORK_PATH%\Unity\src -o %MODULE_PATH%\test\Testmultiply.exe || exit /b