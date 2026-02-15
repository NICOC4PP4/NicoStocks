-- schema.sql (Fase 4 — Portfolio Manager & Intelligent Alerts)

-- 1. Tabla de Activos (Maestro)
CREATE TABLE IF NOT EXISTS assets (
    ticker TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    description TEXT,
    last_price DECIMAL(10, 2),
    pe_ntm DECIMAL(10, 2),
    fcf_share DECIMAL(10, 2),
    avg_buy_price DECIMAL(10, 2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabla de Transacciones
CREATE TABLE IF NOT EXISTS transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker TEXT REFERENCES assets(ticker),
    date DATE NOT NULL,
    type TEXT CHECK (type IN ('BUY', 'SELL', 'DIVIDEND')),
    shares DECIMAL(10, 4),
    price DECIMAL(10, 2),
    amount DECIMAL(12, 2) GENERATED ALWAYS AS (shares * price) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabla de Noticias / Sentimiento
CREATE TABLE IF NOT EXISTS market_news (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker TEXT REFERENCES assets(ticker),
    summary TEXT,
    sentiment DECIMAL(4, 3),
    impact_level TEXT CHECK (impact_level IN ('high', 'med', 'low')),
    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Row Level Security (RLS)
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Enable read access for all users" ON assets
    FOR SELECT USING (true);

CREATE POLICY IF NOT EXISTS "Enable write for service role" ON assets
    FOR ALL USING (auth.role() = 'service_role');

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Enable read access for all users" ON transactions
    FOR SELECT USING (true);

CREATE POLICY IF NOT EXISTS "Enable insert for all users" ON transactions
    FOR INSERT WITH CHECK (true);

ALTER TABLE market_news ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Enable read access for all users" ON market_news
    FOR SELECT USING (true);

-- 5. Migration SQL (ejecutar manualmente si las tablas ya existen)
-- ALTER TABLE assets ADD COLUMN IF NOT EXISTS description TEXT;
-- ALTER TABLE assets ADD COLUMN IF NOT EXISTS avg_buy_price DECIMAL(10, 2);
