-- Enable pgvector extension for embedding storage + HNSW cosine similarity
CREATE EXTENSION IF NOT EXISTS vector;

-- Ensure uuid generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
