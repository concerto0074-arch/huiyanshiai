import os
from flask import g
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ----------------- SQLAlchemy Models -----------------

class UserModel(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PatientModel(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True)
    mean_radius = db.Column(db.Float, nullable=True)
    mean_texture = db.Column(db.Float, nullable=True)
    mean_perimeter = db.Column(db.Float, nullable=True)
    mean_area = db.Column(db.Float, nullable=True)
    mean_smoothness = db.Column(db.Float, nullable=True)
    diagnosis = db.Column(db.String(50), nullable=True)
    probability = db.Column(db.Float, nullable=True)
    risk_level = db.Column(db.String(20), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    analysis = db.Column(db.Text, nullable=True)
    suggestions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
class TenantModel(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------- Compatibility DTOs -----------------

class User:
    def __init__(self, username, password, email, role='user', tenant_id=None, id=None, created_at=None, status='active', age=None, gender=None, phone=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.tenant_id = tenant_id
        self.status = status
        self.age = age
        self.gender = gender
        self.phone = phone
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'tenant_id': self.tenant_id,
            'status': self.status,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.created_at, datetime) else self.created_at
        }
        
def _user_dto(m):
    return User(
        id=m.id, username=m.username, password=m.password, email=m.email, 
        role=m.role, status=m.status, age=m.age, gender=m.gender, 
        phone=m.phone, created_at=m.created_at
    ) if m else None

class Patient:
    def __init__(self, id=None, user_id=None, tenant_id=None, mean_radius=None, mean_texture=None, mean_perimeter=None, mean_area=None, mean_smoothness=None, diagnosis=None, probability=None, risk_level=None, summary=None, analysis=None, suggestions=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.tenant_id = tenant_id
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
            'id': self.id, 'user_id': self.user_id, 'tenant_id': self.tenant_id, 'mean_radius': self.mean_radius,
            'mean_texture': self.mean_texture, 'mean_perimeter': self.mean_perimeter,
            'mean_area': self.mean_area, 'mean_smoothness': self.mean_smoothness,
            'diagnosis': self.diagnosis, 'probability': self.probability, 'risk_level': self.risk_level,
            'summary': self.summary, 'analysis': self.analysis, 'suggestions': self.suggestions,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(self.created_at, datetime) else self.created_at
        }

def _patient_dto(m):
    return Patient(
        id=m.id, user_id=m.user_id, tenant_id=m.tenant_id, mean_radius=m.mean_radius, mean_texture=m.mean_texture,
        mean_perimeter=m.mean_perimeter, mean_area=m.mean_area, mean_smoothness=m.mean_smoothness,
        diagnosis=m.diagnosis, probability=m.probability, risk_level=m.risk_level,
        summary=m.summary, analysis=m.analysis, suggestions=m.suggestions, created_at=m.created_at
    ) if m else None

# ----------------- Database operations -----------------

def init_db():
    db.create_all()

# User ops
def get_user_by_username(username):
    # 多租户过滤：仅在当前租户范围内查找用户
    query = UserModel.query.filter_by(username=username)
    if getattr(g, 'tenant_id', None) is not None:
        query = query.filter_by(tenant_id=g.tenant_id)
    return _user_dto(query.first())

def get_user_by_email(email):
    """
    根据邮箱查询用户，支持多租户过滤

    Args:
        email: 用户邮箱地址

    Returns:
        User DTO 对象 | None（用户不存在时）
    """
    query = UserModel.query.filter_by(email=email)
    if getattr(g, 'tenant_id', None) is not None:
        query = query.filter_by(tenant_id=g.tenant_id)
    return _user_dto(query.first())

def get_user_by_id(user_id):
    query = UserModel.query.filter_by(id=user_id)
    if getattr(g, 'tenant_id', None) is not None:
        query = query.filter_by(tenant_id=g.tenant_id)
    return _user_dto(query.first())

def add_user(user):
    m = UserModel(username=user.username, password=user.password, email=user.email, role=user.role, tenant_id=user.tenant_id, phone=user.phone)
    db.session.add(m)
    db.session.commit()
    return m.id

def get_all_users():
    query = UserModel.query
    if getattr(g, 'tenant_id', None) is not None:
        query = query.filter_by(tenant_id=g.tenant_id)
    return [_user_dto(m) for m in query.order_by(UserModel.created_at.desc()).all()]

def update_user(user_id, data):
    m = UserModel.query.get(user_id)
    if not m: return False
    allowed_fields = {'username', 'password', 'email', 'role', 'status', 'age', 'gender', 'phone', 'tenant_id'}
    for key, val in data.items():
        if key == 'tenant_id':
            # 防止跨租户修改
            continue
        if key in allowed_fields:
            setattr(m, key, val)
    db.session.commit()
    return True

def delete_user(user_id):
    m = UserModel.query.get(user_id)
    if not m: return False
    db.session.delete(m)
    db.session.commit()
    return True

def search_users(keyword='', status='all'):
    q = UserModel.query
    if keyword:
        q = q.filter((UserModel.username.like(f"%{keyword}%")) | (UserModel.email.like(f"%{keyword}%")))
    if status != 'all':
        q = q.filter_by(status=status)
    return [_user_dto(m) for m in q.order_by(UserModel.created_at.desc()).all()]

# Patient ops
def get_all_patients():
    query = PatientModel.query
    if getattr(g, 'tenant_id', None) is not None:
        query = query.filter_by(tenant_id=g.tenant_id)
    return [_patient_dto(m) for m in query.order_by(PatientModel.created_at.desc()).all()]

def get_patient_by_id(patient_id):
    return _patient_dto(PatientModel.query.get(patient_id))

def get_patients_by_date_range(start_date, end_date, user_id=None):
    q = PatientModel.query.filter(PatientModel.created_at >= start_date, PatientModel.created_at <= end_date)
    if user_id:
        q = q.filter_by(user_id=user_id)
    if getattr(g, 'tenant_id', None) is not None:
        q = q.filter_by(tenant_id=g.tenant_id)
    q = PatientModel.query.filter(PatientModel.created_at >= start_date, PatientModel.created_at <= end_date)
    if user_id:
        q = q.filter_by(user_id=user_id)
    return [_patient_dto(m) for m in q.order_by(PatientModel.created_at.desc()).all()]

def get_patients_by_user_id(user_id):
    q = PatientModel.query.filter_by(user_id=user_id)
    if getattr(g, 'tenant_id', None) is not None:
        q = q.filter_by(tenant_id=g.tenant_id)
    return [_patient_dto(m) for m in q.order_by(PatientModel.created_at.desc()).all()]
    return [_patient_dto(m) for m in PatientModel.query.filter_by(user_id=user_id).order_by(PatientModel.created_at.desc()).all()]

def add_patient(patient):
    # 若未显式提供 tenant_id，则使用当前请求的租户上下文
    tenant_id = getattr(g, 'tenant_id', None)
    m = PatientModel(
        user_id=patient.user_id,
        tenant_id=tenant_id if patient.tenant_id is None else patient.tenant_id,
        mean_radius=patient.mean_radius,
        mean_texture=patient.mean_texture,
        mean_perimeter=patient.mean_perimeter,
        mean_area=patient.mean_area,
        mean_smoothness=patient.mean_smoothness,
        diagnosis=patient.diagnosis,
        probability=patient.probability,
        risk_level=patient.risk_level,
        summary=patient.summary,
        analysis=patient.analysis,
        suggestions=patient.suggestions
    )
    db.session.add(m)
    db.session.commit()
    return m.id

def delete_patient(patient_id):
    # 确保只能删除本租户的记录
    q = PatientModel.query.filter_by(id=patient_id)
    if getattr(g, 'tenant_id', None) is not None:
        q = q.filter_by(tenant_id=g.tenant_id)
    m = q.first()
    if not m:
        return False
    db.session.delete(m)
    db.session.commit()
    return True
    m = PatientModel.query.get(patient_id)
    if not m: return False
    db.session.delete(m)
    db.session.commit()
    return True

def get_patient_stats():
    total = PatientModel.query.count()
    high_risk = PatientModel.query.filter_by(risk_level='高风险').count()
    low_risk = PatientModel.query.filter_by(risk_level='低风险').count()
    return {'total': total, 'high_risk': high_risk, 'low_risk': low_risk}
