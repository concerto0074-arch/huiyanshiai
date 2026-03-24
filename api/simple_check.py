import os
print('Current directory:', os.getcwd())
print('patients.db exists:', os.path.exists('patients.db'))
print('File size:', os.path.getsize('patients.db') if os.path.exists('patients.db') else 'N/A')
