# 直接将输出写入文件
with open('test_output.txt', 'w') as f:
    f.write('Hello World!\n')
    f.write('1 + 2 = {}\n'.format(1 + 2))
    f.write('Testing file write function...\n')

# 测试DeepSeek API的导入
with open('test_output.txt', 'a') as f:
    f.write('\n=== Testing DeepSeek API Import ===\n')
    try:
        import requests
        f.write('✓ requests module imported successfully\n')
    except ImportError as e:
        f.write('✗ requests module import failed: {}\n'.format(e))

print('Script executed. Check test_output.txt for results.')
