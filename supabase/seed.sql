-- =========================================================================
-- 慧眼识癌 - 初始化种子数据
-- 在 Supabase Dashboard → SQL Editor 中执行本脚本
-- =========================================================================

-- 1. 插入默认租户（如果不存在）
INSERT INTO public.tenants (name)
VALUES ('慧眼识癌官方体验中心')
ON CONFLICT DO NOTHING;

-- 2. 如果已有 users 表但缺少 plan 字段，执行以下 ALTER（幂等）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'plan'
    ) THEN
        ALTER TABLE public.users ADD COLUMN plan VARCHAR(20) DEFAULT 'free';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'plan_expire_at'
    ) THEN
        ALTER TABLE public.users ADD COLUMN plan_expire_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- 3. 插入默认管理员账户（bcrypt 哈希密码: admin123）
--    如果 username='admin' 已存在则跳过
INSERT INTO public.users (username, email, password, role, phone, plan, tenant_id)
SELECT
    'admin',
    'admin@huiyanshiai.com',
    '$2b$12$QQR4eK2rucb7u8NRlpuqZ.5bsqOxnpDA7ZssWjG4/dwNLnPJHmiIi',
    'admin',
    '',
    'premium',
    (SELECT id FROM public.tenants WHERE name = '慧眼识癌官方体验中心' LIMIT 1)
WHERE NOT EXISTS (
    SELECT 1 FROM public.users WHERE username = 'admin'
);

-- 验证插入结果
SELECT id, username, email, role, plan, created_at FROM public.users;
