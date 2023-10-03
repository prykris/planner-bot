@echo off

git pull -X theirs > gitpull.log

if %errorlevel% == 0 (
  findstr /c:"Already up-to-date" gitpull.log > nul
  if %errorlevel% == 0 (
    echo No updates, already up to date
  ) else (
    echo Pull updated repository successfully
  )
) else (
  echo Error occurred during git pull
)

pause