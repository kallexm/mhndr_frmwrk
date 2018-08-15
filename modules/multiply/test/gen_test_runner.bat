@echo off

set MODULE_PATH=%~dp0\..
set FRAMEWORK_PATH=%~dp0\..\..\framework

ruby %FRAMEWORK_PATH%\Unity\auto\generate_test_runner.rb %MODULE_PATH%\test\Testmultiply.c %MODULE_PATH%\test\Testmultiply_Runner.c