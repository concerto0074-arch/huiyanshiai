-- Supabase / PostgreSQL 初始化专属建表脚本 (SaaS多租户版)
-- 支持医院/机构物理隔离的架构
-- 建议按顺序在 Supabase SQL Editor 中执行

-- =========================================================================
-- 1. 创建机构/租户表 (tenants)
-- 作用：所有业务数据的隔离基座，每个医院对应一条记录
-- =========================================================================
CREATE TABLE IF NOT EXISTS public.tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) UNIQUE NOT NULL,    -- 医院/机构名称
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 加速机构名称的检索
CREATE INDEX IF NOT EXISTS idx_tenants_name ON public.tenants(name);


-- =========================================================================
-- 2. 创建用户表 (users)
-- 作用：包含医生、管理员、患者账号，并使用 tenant_id 进行归属隔离
-- =========================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    role VARCHAR(20) DEFAULT 'user',      -- user, admin, doctor 等
    status VARCHAR(20) DEFAULT 'active',  -- active, banned 等
    age INTEGER,
    gender VARCHAR(20),
    phone VARCHAR(20),
    tenant_id INTEGER REFERENCES public.tenants(id) ON DELETE SET NULL, -- 归属的租户机构
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以加速登录校验和按租户过滤用户
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON public.users(tenant_id);


-- =========================================================================
-- 3. 创建患者问诊/预测记录表 (patients)
-- 作用：记录每次大模型预测诊断流水，受双重约束 (用户 + 租户机构)
-- =========================================================================
CREATE TABLE IF NOT EXISTS public.patients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES public.users(id) ON DELETE SET NULL,     -- 是哪个用户的记录
    tenant_id INTEGER REFERENCES public.tenants(id) ON DELETE SET NULL, -- 这条记录属于哪个医院
    mean_radius DOUBLE PRECISION,
    mean_texture DOUBLE PRECISION,
    mean_perimeter DOUBLE PRECISION,
    mean_area DOUBLE PRECISION,
    mean_smoothness DOUBLE PRECISION,
    diagnosis VARCHAR(50),
    probability DOUBLE PRECISION,
    risk_level VARCHAR(20),
    summary TEXT,
    analysis TEXT,
    suggestions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以加速按用户和按租户查询历史记录
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON public.patients(user_id);
CREATE INDEX IF NOT EXISTS idx_patients_tenant_id ON public.patients(tenant_id);

-- =========================================================================
-- 4. 插入默认的测试租户和超级管理员 (可选)
-- 建议在建表后直接运行这几句进行测试环境兜底
-- =========================================================================
INSERT INTO public.tenants (name) VALUES ('慧眼识癌官方体验中心') ON CONFLICT DO NOTHING;
