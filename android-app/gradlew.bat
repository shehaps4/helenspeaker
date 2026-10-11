@rem Iraqi AI Smart Speaker Gradle Runner
@echo off
set "GRADLE_BIN=C:\Users\Th3painter\.gradle\wrapper\dists\gradle-8.14-all\c2qonpi39x1mddn7hk5gh9iqj\gradle-8.14\bin\gradle.bat"
if exist "%GRADLE_BIN%" (
    "%GRADLE_BIN%" %*
) else (
    gradle %*
)
