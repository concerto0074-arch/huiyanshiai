@echo off

REM 简单的批处理文件，用于执行DeepSeek API测试脚本
echo 开始执行DeepSeek API测试...
echo 执行时间: %date% %time%

REM 执行Python脚本并将输出重定向到文件
python test_deepseek.py > deepseek_test_log.txt 2>&1

REM 检查执行结果
if %ERRORLEVEL% == 0 (
    echo Python脚本执行成功！
    echo 查看测试日志: deepseek_test_log.txt
) else (
    echo Python脚本执行失败，错误码: %ERRORLEVEL%
)

echo 测试完成！
