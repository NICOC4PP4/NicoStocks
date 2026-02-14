-- schema.sql (Actualizado para Fase 1.6)

-- 1. Limpieza inicial (Opcional, cuidado en producción)
-- DROP TABLE IF EXISTS market_news;
-- DROP TABLE IF EXISTS transactions;
-- DROP TABLE IF EXISTS assets;

-- 2. Tabla de Activos (Maestro)
CREATE TABLE IF NOT EXISTS assets (
    ticker TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    last_price DECIMAL(10, 2),
    pe_ntm DECIMAL(10, 2),
    fcf_share DECIMAL(10, 2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabla de Transacciones
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

-- 4. Tabla de Noticias / Sentimiento
CREATE TABLE IF NOT EXISTS market_news (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    ticker TEXT REFERENCES assets(ticker),
    summary TEXT,
    sentiment DECIMAL(4, 3), -- -1 a 1
    impact_level TEXT CHECK (impact_level IN ('high', 'med', 'low')),
    published_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Row Level Security (RLS) - Permisivo para Desarrollo WEB
-- IMPORTANTE: Habilitamos acceso público de LECTURA para que el Dashboard funcione sin Auth complejo por ahora.
-- La escritura idealmente se hace con el SERVICE_ROLE KEY desde los scripts de backend.

-- Assets
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON assets
    FOR SELECT USING (true);

CREATE POLICY "Enable insert/update for service role only" ON assets
    FOR ALL USING (auth.role() = 'service_role');

-- Transactions
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON transactions
    FOR SELECT USING (true);

-- Market News
ALTER TABLE market_news ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON market_news
    FOR SELECT USING (true);
