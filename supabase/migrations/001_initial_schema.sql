-- ============================================================================
-- AI RENTAL COPYWRITER — Schema Inicial
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================================
-- TABELA: niches
-- ============================================================================
CREATE TABLE niches (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  description TEXT,
  color TEXT NOT NULL DEFAULT '#6366f1',
  icon_name TEXT DEFAULT 'folder',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABELA: vibes
-- ============================================================================
CREATE TABLE vibes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  slug TEXT NOT NULL UNIQUE,
  description TEXT NOT NULL,
  prompt_modifier TEXT NOT NULL,
  examples TEXT,
  sort_order INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- TABELA: assets
-- ============================================================================
CREATE TABLE assets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  file_name TEXT NOT NULL,
  file_type TEXT NOT NULL CHECK (file_type IN ('pdf', 'audio', 'video')),
  file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes > 0),
  storage_path TEXT NOT NULL UNIQUE,
  mime_type TEXT NOT NULL,
  processing_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
  processing_error TEXT,
  processing_started_at TIMESTAMPTZ,
  processing_completed_at TIMESTAMPTZ,
  markdown_content TEXT,
  content_summary TEXT,
  word_count INTEGER,
  niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assets_niche ON assets(niche_id);
CREATE INDEX idx_assets_status ON assets(processing_status);
CREATE INDEX idx_assets_type ON assets(file_type);
CREATE INDEX idx_assets_created ON assets(created_at DESC);

-- ============================================================================
-- TABELA: embeddings (pgvector)
-- ============================================================================
CREATE TABLE embeddings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  embedding vector(1536) NOT NULL,
  asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_hash TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,
  chunk_size INTEGER NOT NULL,
  niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
  source_type TEXT NOT NULL CHECK (source_type IN ('pdf', 'audio', 'video')),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(asset_id, chunk_hash)
);

CREATE INDEX idx_embeddings_asset ON embeddings(asset_id);
CREATE INDEX idx_embeddings_niche ON embeddings(niche_id);
CREATE INDEX idx_embeddings_vector ON embeddings
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- ============================================================================
-- TABELA: generations
-- ============================================================================
CREATE TABLE generations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  briefing_text TEXT NOT NULL,
  niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
  vibe_id UUID REFERENCES vibes(id) ON DELETE SET NULL,
  rag_context JSONB,
  options JSONB NOT NULL DEFAULT '[]',
  judge_feedback JSONB,
  status TEXT NOT NULL DEFAULT 'generating'
    CHECK (status IN ('generating', 'completed', 'failed')),
  retry_count INTEGER NOT NULL DEFAULT 0,
  error_message TEXT,
  generation_time_ms INTEGER,
  tokens_used INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_gen_niche ON generations(niche_id);
CREATE INDEX idx_gen_vibe ON generations(vibe_id);
CREATE INDEX idx_gen_status ON generations(status);
CREATE INDEX idx_gen_created ON generations(created_at DESC);

-- ============================================================================
-- TABELA: slides
-- ============================================================================
CREATE TABLE slides (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  generation_id UUID NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  option_index INTEGER NOT NULL CHECK (option_index BETWEEN 0 AND 2),
  slide_number INTEGER NOT NULL CHECK (slide_number BETWEEN 1 AND 7),
  slide_type TEXT NOT NULL CHECK (slide_type IN (
    'hook', 'dor', 'solucao', 'prova', 'beneficio', 'objecao', 'cta'
  )),
  headline TEXT NOT NULL,
  body_text TEXT NOT NULL DEFAULT '',
  visual_hint TEXT,
  is_edited BOOLEAN NOT NULL DEFAULT false,
  original_headline TEXT,
  original_body_text TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(generation_id, option_index, slide_number)
);

CREATE INDEX idx_slides_gen ON slides(generation_id);

-- ============================================================================
-- TABELA: winners (few-shot learning)
-- ============================================================================
CREATE TABLE winners (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  generation_id UUID NOT NULL REFERENCES generations(id) ON DELETE CASCADE,
  option_index INTEGER NOT NULL CHECK (option_index BETWEEN 0 AND 2),
  performance_notes TEXT,
  performance_metrics JSONB,
  times_used_in_fewshot INTEGER NOT NULL DEFAULT 0,
  last_used_at TIMESTAMPTZ,
  niche_id UUID NOT NULL REFERENCES niches(id),
  vibe_id UUID NOT NULL REFERENCES vibes(id),
  full_carousel_json JSONB NOT NULL,
  marked_winner_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(generation_id, option_index)
);

CREATE INDEX idx_winners_niche_vibe ON winners(niche_id, vibe_id, times_used_in_fewshot);

-- ============================================================================
-- TRIGGER: auto-update updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_niches BEFORE UPDATE ON niches FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_vibes BEFORE UPDATE ON vibes FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_assets BEFORE UPDATE ON assets FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_generations BEFORE UPDATE ON generations FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_slides BEFORE UPDATE ON slides FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER trg_winners BEFORE UPDATE ON winners FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================================
-- FUNÇÃO: Busca semântica por similaridade
-- ============================================================================
CREATE OR REPLACE FUNCTION search_similar_embeddings(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5,
  filter_niche_id uuid DEFAULT NULL
)
RETURNS TABLE (
  id uuid, asset_id uuid, chunk_text text, similarity float, niche_id uuid, source_type text, metadata jsonb
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT e.id, e.asset_id, e.chunk_text,
    1 - (e.embedding <=> query_embedding) as similarity,
    e.niche_id, e.source_type, e.metadata
  FROM embeddings e
  WHERE (filter_niche_id IS NULL OR e.niche_id = filter_niche_id)
    AND 1 - (e.embedding <=> query_embedding) > match_threshold
  ORDER BY e.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================================================
-- FUNÇÃO: Few-shot examples (winners)
-- ============================================================================
CREATE OR REPLACE FUNCTION get_fewshot_examples(
  p_niche_id uuid, p_vibe_id uuid, max_examples int DEFAULT 3
)
RETURNS TABLE (
  winner_id uuid, carousel_json jsonb, performance_notes text,
  times_used integer, marked_winner_at timestamptz
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT w.id, w.full_carousel_json, w.performance_notes,
    w.times_used_in_fewshot, w.marked_winner_at
  FROM winners w
  WHERE w.niche_id = p_niche_id AND w.vibe_id = p_vibe_id
  ORDER BY w.times_used_in_fewshot ASC, w.marked_winner_at DESC
  LIMIT max_examples;

  UPDATE winners SET times_used_in_fewshot = times_used_in_fewshot + 1, last_used_at = NOW()
  WHERE id IN (
    SELECT w2.id FROM winners w2
    WHERE w2.niche_id = p_niche_id AND w2.vibe_id = p_vibe_id
    ORDER BY w2.times_used_in_fewshot ASC, w2.marked_winner_at DESC
    LIMIT max_examples
  );
END;
$$;

-- ============================================================================
-- VIEWS
-- ============================================================================
CREATE OR REPLACE VIEW assets_with_stats AS
SELECT a.*, n.name as niche_name, n.color as niche_color,
  COUNT(e.id) as embedding_count
FROM assets a
LEFT JOIN niches n ON a.niche_id = n.id
LEFT JOIN embeddings e ON a.id = e.asset_id
GROUP BY a.id, n.name, n.color;

CREATE OR REPLACE VIEW generations_with_context AS
SELECT g.*, n.name as niche_name, n.color as niche_color,
  v.name as vibe_name, v.slug as vibe_slug,
  (SELECT COUNT(*) FROM winners WHERE generation_id = g.id) as winners_count
FROM generations g
LEFT JOIN niches n ON g.niche_id = n.id
LEFT JOIN vibes v ON g.vibe_id = v.id;

-- ============================================================================
-- RLS
-- ============================================================================
ALTER TABLE niches ENABLE ROW LEVEL SECURITY;
ALTER TABLE vibes ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE slides ENABLE ROW LEVEL SECURITY;
ALTER TABLE winners ENABLE ROW LEVEL SECURITY;

CREATE POLICY "allow_all" ON niches FOR ALL USING (true);
CREATE POLICY "allow_all" ON vibes FOR ALL USING (true);
CREATE POLICY "allow_all" ON assets FOR ALL USING (true);
CREATE POLICY "allow_all" ON embeddings FOR ALL USING (true);
CREATE POLICY "allow_all" ON generations FOR ALL USING (true);
CREATE POLICY "allow_all" ON slides FOR ALL USING (true);
CREATE POLICY "allow_all" ON winners FOR ALL USING (true);

-- ============================================================================
-- SEED: Nichos
-- ============================================================================
INSERT INTO niches (name, slug, description, color, icon_name) VALUES
  ('Construção Civil', 'construcao-civil', 'Equipamentos e maquinário para construção', '#f97316', 'hard-hat'),
  ('Veículos', 'veiculos', 'Carros, motos, vans e veículos comerciais', '#3b82f6', 'car'),
  ('Tecnologia', 'tecnologia', 'Equipamentos de TI, servidores, notebooks', '#8b5cf6', 'laptop'),
  ('Eventos', 'eventos', 'Som, iluminação, stands e estruturas', '#ec4899', 'sparkles'),
  ('Imóveis Residenciais', 'imoveis-residenciais', 'Casas, apartamentos, quitinetes', '#10b981', 'home'),
  ('Imóveis Comerciais', 'imoveis-comerciais', 'Escritórios, lojas, galpões', '#6366f1', 'building'),
  ('Equipamentos Industriais', 'equipamentos-industriais', 'Maquinário industrial pesado', '#ef4444', 'cog'),
  ('Ferramentas', 'ferramentas', 'Ferramentas manuais e elétricas', '#f59e0b', 'wrench'),
  ('Jardinagem', 'jardinagem', 'Equipamentos para paisagismo', '#22c55e', 'flower-2'),
  ('Esportes e Lazer', 'esportes-lazer', 'Equipamentos esportivos', '#06b6d4', 'bike')
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- SEED: Vibes
-- ============================================================================
INSERT INTO vibes (name, slug, description, prompt_modifier, examples, sort_order) VALUES
  ('Educativo', 'educativo',
   'Tom didático e informativo',
   'Escreva em tom educativo e didático. Use dados, estatísticas e explicações claras. Posicione-se como especialista que ensina.',
   '["Você sabia que...", "Aqui está o que poucos sabem:", "3 passos para entender"]', 1),
  ('Urgente', 'urgente',
   'Tom de urgência e escassez',
   'Escreva com senso de urgência. Use escassez, prazos, oportunidades limitadas. Crie FOMO. CTAs diretos e imediatos.',
   '["Última chance", "Só até sexta", "Vagas limitadas", "Não perca"]', 2),
  ('Autoridade', 'autoridade',
   'Tom de especialista confiável',
   'Escreva como autoridade no assunto. Use experiência, cases, provas sociais e resultados concretos. Tom seguro e confiante.',
   '["Com mais de 10 anos", "Já ajudamos +500", "Referência no mercado"]', 3),
  ('Provocativo', 'provocativo',
   'Tom desafiador que provoca reflexão',
   'Escreva de forma provocativa. Questione crenças comuns, confronte mitos, use linguagem direta e impactante.',
   '["Pare de acreditar que...", "A verdade que ninguém conta", "Você está fazendo errado"]', 4)
ON CONFLICT (slug) DO NOTHING;
