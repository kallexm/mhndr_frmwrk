@echo off

set MODULE_PATH=%~dp0\..

ruby %FRAMEWORK_PATH%\Unity\auto\generate_module.rb -i%MODULE_PATH% -s%MODULE_PATH% -t%MODULE_PATH%\test multiply