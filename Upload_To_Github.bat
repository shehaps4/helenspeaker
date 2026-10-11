@echo off
title Push to GitHub - Helen Iraqi Smart Speaker
cd /d "%~dp0"
echo =======================================================
echo  جاري رفع جميع ملفات هيلين إلى مستودع GitHub...
echo  https://github.com/shehaps4/helenspeaker
echo =======================================================
git push -u origin main
echo =======================================================
echo  تم الانتهاء! اضغط أي مفتاح للإغلاق.
pause
