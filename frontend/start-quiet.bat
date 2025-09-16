@echo off
REM Start React app with suppressed Node.js warnings
set NODE_NO_WARNINGS=1
set NODE_OPTIONS=--no-deprecation
npm run start-verbose
