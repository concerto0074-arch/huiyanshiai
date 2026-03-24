import glob

nav_css = r'''
        /* 导航栏补充样式 */
        .navbar-brand {
            display: flex !important;
            align-items: center;
            gap: 12px;
            color: #007BFF !important;
            text-decoration: none;
            padding: 0;
            margin-right: 30px;
        }
        .logo-icon {
            font-size: 2.2rem;
            color: #007BFF;
            text-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
            transition: transform 0.3s ease;
        }
        .navbar-brand:hover .logo-icon { transform: scale(1.1); }
        .brand-text {
            display: flex;
            flex-direction: column;
            line-height: 1.1;
        }
        .brand-main {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: 1px;
            background: linear-gradient(135deg, #007BFF, #00B4DB);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-sub {
            font-size: 0.75rem;
            color: #6c757d;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        .navbar-right {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .notification-icon {
            position: relative;
            color: #495057;
            font-size: 1.2rem;
            transition: all 0.3s ease;
            text-decoration: none !important;
        }
        .notification-icon:hover { color: #007BFF; text-decoration: none; }
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -8px;
            background-color: #dc3545;
            color: white;
            border-radius: 50%;
            padding: 2px 5px;
            font-size: 0.6rem;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(220,53,69,0.3);
        }
        .login-btn {
            background-color: #007BFF;
            color: white;
            border: none;
            padding: 6px 20px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(0,123,255,0.2);
            cursor: pointer;
            outline: none;
        }
        .login-btn:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,123,255,0.3);
            color: white;
            outline: none;
        }
        .login-btn:focus { outline: none; }
        .navbar-nav { gap: 10px; }
'''

files = glob.glob('d:\\huiyanshiai(2.0)\\frontend\\article-detail-*.html')
for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if '/* 导航栏补充样式 */' not in content:
        # inject before closing style tag
        content = content.replace('</style>', nav_css + '\n    </style>')
        
        # also update navbar items wrapper spacing class if needed
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print(f"Fixed {len(files)} article files.")
