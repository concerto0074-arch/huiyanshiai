@echo off
echo 开始运行测试脚本...
python basic_test.py > basic_test_output.txt
if exist basic_test_output.txt (
    echo 测试脚本运行完成，输出已保存到 basic_test_output.txt
    type basic_test_output.txt
) else (
    echo 测试脚本运行失败，没有生成输出文件
)

echo.
echo 运行DeepSeek简单测试...
python simple_deepseek_test.py > deepseek_test_output.txt
if exist deepseek_test_output.txt (
    echo DeepSeek测试完成，输出已保存到 deepseek_test_output.txt
    type deepseek_test_output.txt
) else (
    echo DeepSeek测试失败，没有生成输出文件
)

echo.
echo 所有测试完成
pause