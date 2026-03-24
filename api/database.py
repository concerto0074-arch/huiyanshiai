import sqlite3
import json
from datetime import datetime

# 数据库配置
DATABASE = 'patients.db'

# 初始化数据库

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建用户表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            age INTEGER,
            gender TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建患者表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mean_radius REAL,
            mean_texture REAL,
            mean_perimeter REAL,
            mean_area REAL,
            mean_smoothness REAL,
            diagnosis TEXT,
            probability REAL,
            risk_level TEXT,
            summary TEXT,
            analysis TEXT,
            suggestions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    migrate_db()
    conn.close()

def migrate_db():
    """Add missing columns to existing users table for backward compatibility."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    # 定义需要确保存在的列及其类型和默认值
    required = [
        ("role", "TEXT", "'user'"),
        ("status", "TEXT", "'active'"),
        ("age", "INTEGER", "NULL"),
        ("gender", "TEXT", "NULL"),
        ("phone", "TEXT", "NULL"),
    ]
    for col_name, col_type, default in required:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type} DEFAULT {default}")
    conn.commit()
    conn.close()

# 用户记录类

class User:
    def __init__(self, username, password, email, role='user', id=None, created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role = role  # 添加角色属性
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,  # 返回角色信息
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.created_at, datetime) else self.created_at
        }

# 患者记录类

class Patient:
    def __init__(self, user_id, mean_radius, mean_texture, mean_perimeter, mean_area, 
                 mean_smoothness, diagnosis, probability, risk_level, 
                 summary, analysis, suggestions, id=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.mean_radius = mean_radius
        self.mean_texture = mean_texture
        self.mean_perimeter = mean_perimeter
        self.mean_area = mean_area
        self.mean_smoothness = mean_smoothness
        self.diagnosis = diagnosis
        self.probability = probability
        self.risk_level = risk_level
        self.summary = summary
        self.analysis = analysis
        self.suggestions = suggestions
        self.created_at = created_at or datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'mean_radius': self.mean_radius,
            'mean_texture': self.mean_texture,
            'mean_perimeter': self.mean_perimeter,
            'mean_area': self.mean_area,
            'mean_smoothness': self.mean_smoothness,
            'diagnosis': self.diagnosis,
            'probability': self.probability,
            'risk_level': self.risk_level,
            'summary': self.summary,
            'analysis': self.analysis,
            'suggestions': self.suggestions,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if isinstance(self.created_at, datetime) else self.created_at
        }

# 用户数据操作函数

def get_user_by_id(user_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row:
        user = User(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            email=row['email'],
            role=row['role'],  # 添加角色字段
            created_at=row['created_at']
        )
        conn.close()
        return user
    else:
        conn.close()
        return None

def get_user_by_username(username):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    if row:
        user = User(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            email=row['email'],
            role=row['role'],  # 添加角色字段
            created_at=row['created_at']
        )
        conn.close()
        return user
    else:
        conn.close()
        return None

def add_user(user):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (username, password, email, role)
        VALUES (?, ?, ?, ?)
    ''', (user.username, user.password, user.email, user.role))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

# 患者数据操作函数

def get_all_patients():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients ORDER BY created_at DESC')
    
    rows = cursor.fetchall()
    
    patients = []
    for row in rows:
        patients.append(Patient(
            id=row['id'],
            user_id=row['user_id'],
            mean_radius=row['mean_radius'],
            mean_texture=row['mean_texture'],
            mean_perimeter=row['mean_perimeter'],
            mean_area=row['mean_area'],
            mean_smoothness=row['mean_smoothness'],
            diagnosis=row['diagnosis'],
            probability=row['probability'],
            risk_level=row['risk_level'],
            summary=row['summary'],
            analysis=row['analysis'],
            suggestions=row['suggestions'],
            created_at=row['created_at']
        ))
    
    conn.close()
    return patients

def get_patient_by_id(patient_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    row = cursor.fetchone()
    
    if row:
        patient = Patient(
            id=row['id'],
            user_id=row['user_id'],  # 添加user_id
            mean_radius=row['mean_radius'],
            mean_texture=row['mean_texture'],
            mean_perimeter=row['mean_perimeter'],
            mean_area=row['mean_area'],
            mean_smoothness=row['mean_smoothness'],
            diagnosis=row['diagnosis'],
            probability=row['probability'],
            risk_level=row['risk_level'],
            summary=row['summary'],
            analysis=row['analysis'],
            suggestions=row['suggestions'],
            created_at=row['created_at']
        )
        conn.close()
        return patient
    else:
        conn.close()
        return None

# 按日期范围获取患者记录
def get_patients_by_date_range(start_date, end_date, user_id=None):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('''
            SELECT * FROM patients 
            WHERE user_id = ? AND created_at BETWEEN ? AND ? 
            ORDER BY created_at DESC
        ''', (user_id, start_date, end_date))
    else:
        cursor.execute('''
            SELECT * FROM patients 
            WHERE created_at BETWEEN ? AND ? 
            ORDER BY created_at DESC
        ''', (start_date, end_date))
    
    rows = cursor.fetchall()
    patients = []
    for row in rows:
        patients.append(Patient(
            id=row['id'],
            user_id=row['user_id'],
            mean_radius=row['mean_radius'],
            mean_texture=row['mean_texture'],
            mean_perimeter=row['mean_perimeter'],
            mean_area=row['mean_area'],
            mean_smoothness=row['mean_smoothness'],
            diagnosis=row['diagnosis'],
            probability=row['probability'],
            risk_level=row['risk_level'],
            summary=row['summary'],
            analysis=row['analysis'],
            suggestions=row['suggestions'],
            created_at=row['created_at']
        ))
    
    conn.close()
    return patients

# 按用户ID获取患者记录
def get_patients_by_user_id(user_id):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM patients WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cursor.fetchall()
    
    patients = []
    for row in rows:
        patients.append(Patient(
            id=row['id'],
            user_id=row['user_id'],
            mean_radius=row['mean_radius'],
            mean_texture=row['mean_texture'],
            mean_perimeter=row['mean_perimeter'],
            mean_area=row['mean_area'],
            mean_smoothness=row['mean_smoothness'],
            diagnosis=row['diagnosis'],
            probability=row['probability'],
            risk_level=row['risk_level'],
            summary=row['summary'],
            analysis=row['analysis'],
            suggestions=row['suggestions'],
            created_at=row['created_at']
        ))
    
    conn.close()
    return patients

# 获取所有用户
def get_all_users():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    rows = cursor.fetchall()

    users = []
    for row in rows:
        # Safely get role, default to 'user' if column missing
        try:
            role = row['role']
        except Exception:
            role = 'user'
        users.append(User(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            email=row['email'],
            role=role,
            created_at=row['created_at']
        ))

    conn.close()
    return users

def add_patient(patient):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO patients (user_id, mean_radius, mean_texture, mean_perimeter, mean_area, 
                             mean_smoothness, diagnosis, probability, risk_level, 
                             summary, analysis, suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        patient.user_id, patient.mean_radius, patient.mean_texture, patient.mean_perimeter, patient.mean_area, 
        patient.mean_smoothness, patient.diagnosis, patient.probability, patient.risk_level, 
        patient.summary, patient.analysis, patient.suggestions
    ))
    
    patient_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return patient_id

def delete_patient(patient_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    affected_rows = cursor.rowcount
    
    conn.commit()
    conn.close()
    return affected_rows > 0

def get_patient_stats():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM patients')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM patients WHERE risk_level = ?', ('高风险',))
    high_risk = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM patients WHERE risk_level = ?', ('低风险',))
    low_risk = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total,
        'high_risk': high_risk,
        'low_risk': low_risk
    }

# 数据库迁移函数，确保用户表拥有最新列（幂等）
def migrate_db():
    """Add missing columns to users table for backward compatibility."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(users)')
    # column name is at index 1 in the PRAGMA result tuple
    existing = {row[1] for row in cursor.fetchall()}
    required = [
        ('role', "TEXT DEFAULT 'user'"),
        ('status', "TEXT DEFAULT 'active'"),
        ('age', "INTEGER"),
        ('gender', "TEXT"),
        ('phone', "TEXT")
    ]
    for col, definition in required:
        if col not in existing:
            try:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {col} {definition}')
                print(f'已为 users 表添加列 {col}')
            except Exception as e:
                print(f'添加列 {col} 失败: {e}')
    conn.commit()
    conn.close()

# 更新用户信息
def update_user(user_id, data):
    """根据 data dict 更新用户字段，返回是否成功"""
    allowed_fields = {'username', 'password', 'email', 'role', 'status', 'age', 'gender', 'phone'}
    fields = []
    values = []
    for key, value in data.items():
        if key in allowed_fields:
            fields.append(f"{key} = ?")
            values.append(value)
    if not fields:
        return False
    values.append(user_id)
    set_clause = ", ".join(fields)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

# 删除用户
def delete_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

# 搜索用户（支持关键词和状态过滤）
def search_users(keyword='', status='all'):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = 'SELECT * FROM users WHERE 1=1'
    params = []
    if keyword:
        query += ' AND (username LIKE ? OR email LIKE ?)' 
        kw = f"%{keyword}%"
        params.extend([kw, kw])
    if status != 'all':
        query += ' AND status = ?'
        params.append(status)
    query += ' ORDER BY created_at DESC'
    cursor.execute(query, params)
    rows = cursor.fetchall()
    users = []
    for row in rows:
        users.append(User(
            id=row['id'],
            username=row['username'],
            password=row['password'],
            email=row['email'],
            role=row['role'],
            created_at=row['created_at']
        ))
    conn.close()
    return users
