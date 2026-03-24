@echo off

echo Starting basic test...
python basic_test.py > basic_test_output.txt
if exist basic_test_output.txt (
    echo Basic test completed, output saved to basic_test_output.txt
    type basic_test_output.txt
) else (
    echo Basic test failed, no output file generated
)

echo.
echo Starting DeepSeek test...
python simple_deepseek_test.py > deepseek_test_output.txt
if exist deepseek_test_output.txt (
    echo DeepSeek test completed, output saved to deepseek_test_output.txt
    type deepseek_test_output.txt
) else (
    echo DeepSeek test failed, no output file generated
)

echo.
echo All tests completed
pause
