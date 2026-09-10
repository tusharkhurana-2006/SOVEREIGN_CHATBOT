"""
================================================================================
SOVEREIGN PYTHON RAG PIPELINE // PURE-PYTHON VECTOR & SEMANTIC ENGINE
Air-Gapped, Zero-External-Dependency Hybrid Vector Index & Similarity Search
================================================================================
"""

import math
import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional

# Standard English stopwords (filtered for prose while preserving technical tokens)
STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
    'any', 'are', 'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being',
    'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t',
    'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during',
    'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t',
    'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here',
    'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it',
    'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my',
    'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other',
    'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t',
    'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some',
    'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves',
    'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re',
    'they\'ve', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up',
    'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were',
    'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which',
    'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would',
    'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours',
    'yourself', 'yourselves'
}


class Chunk:
    def __init__(self, chunk_id: str, doc_id: str, title: str, text: str, metadata: Dict[str, Any]):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.title = title
        self.text = text
        self.metadata = metadata
        self.tokens = []
        self.tf = {}
        self.dense_vector = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": self.title,
            "text": self.text,
            "metadata": self.metadata,
            "token_count": len(self.tokens)
        }


class SovereignVectorEngine:
    """
    Pure Python Hybrid Vector Index & Semantic Retrieval System.
    Combines:
    1. Lexical BM25/TF-IDF Exact Matching for credential names, ports, env keys, IDs.
    2. Dense Subword & Feature Hash Embeddings for natural language semantic query matching.
    """
    def __init__(self, embedding_dim: int = 128, hybrid_alpha: float = 0.65):
        self.embedding_dim = embedding_dim
        self.hybrid_alpha = hybrid_alpha  # Weight for dense vs lexical
        self.chunks: List[Chunk] = []
        self.doc_freq: Dict[str, int] = {}
        self.total_docs: int = 0
        self.is_indexed: bool = False

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenizes text while carefully preserving technical tokens,
        URLs, camelCase keys, ENV_VARS, and dotted identifiers.
        """
        # Extract alphanumeric words and special symbols
        raw_tokens = re.findall(r'[A-Za-z0-9_\-\.\:\/\@]+', text.lower())
        tokens = []
        for tok in raw_tokens:
            # Strip trailing punctuation
            clean = tok.strip('.,:;()[]{}')
            if clean and (clean not in STOPWORDS or len(clean) > 4 or '_' in clean or '-' in clean):
                tokens.append(clean)
                # If token has underscores or dots, also index the sub-parts
                if '_' in clean:
                    tokens.extend([p for p in clean.split('_') if p and p not in STOPWORDS])
                if '-' in clean:
                    tokens.extend([p for p in clean.split('-') if p and p not in STOPWORDS])
                if '.' in clean:
                    tokens.extend([p for p in clean.split('.') if p and p not in STOPWORDS])
        return tokens

    def _generate_dense_embedding(self, text: str) -> List[float]:
        """
        Pure Python High-Dimensional Semantic Feature Hashing Vectorizer.
        Generates normalized unit vectors based on character 3-grams, 4-grams, and word tokens.
        """
        vector = [0.0] * self.embedding_dim
        norm_text = text.lower()
        
        # 1. Word level hashing
        words = self.tokenize(norm_text)
        for w in words:
            # Hash to index and sign
            h = int(hashlib.md5(w.encode('utf-8')).hexdigest(), 16)
            idx = h % self.embedding_dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vector[idx] += sign * 1.5

        # 2. Character n-gram hashing (captures typos, subwords, API key prefixes)
        for n in (3, 4):
            if len(norm_text) >= n:
                for i in range(len(norm_text) - n + 1):
                    ngram = norm_text[i:i+n]
                    h = int(hashlib.sha256(ngram.encode('utf-8')).hexdigest(), 16)
                    idx = h % self.embedding_dim
                    sign = 1.0 if ((h >> 8) & 1) else -1.0
                    vector[idx] += sign * 0.5

        # 3. L2 Normalization
        magnitude = math.sqrt(sum(v * v for v in vector))
        if magnitude > 1e-9:
            vector = [v / magnitude for v in vector]
        return vector

    @staticmethod
    def chunk_document(doc_id: str, title: str, content: str, metadata: Dict[str, Any], max_chunk_size: int = 400, overlap: int = 80) -> List[Chunk]:
        """
        Splits a document into structured, overlapping semantic chunks.
        Respects section headers and key-value blocks.
        """
        chunks = []
        # Check if content has clear markdown sections
        sections = re.split(r'\n(?=#{1,4}\s+)', content)
        chunk_idx = 0

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # If section fits in chunk size, keep it as a clean semantic block
            if len(section) <= max_chunk_size:
                cid = f"{doc_id}_c{chunk_idx}"
                chunks.append(Chunk(cid, doc_id, title, section, metadata))
                chunk_idx += 1
            else:
                # Sliding window chunking
                words = section.split()
                start = 0
                while start < len(words):
                    end = min(len(words), start + 60)
                    chunk_text = " ".join(words[start:end])
                    cid = f"{doc_id}_c{chunk_idx}"
                    chunks.append(Chunk(cid, doc_id, title, chunk_text, metadata))
                    chunk_idx += 1
                    if end == len(words):
                        break
                    start += 45  # Overlap

        return chunks

    def add_chunks(self, new_chunks: List[Chunk]):
        """Adds chunks to the vector engine and triggers re-indexing."""
        for chunk in new_chunks:
            chunk.tokens = self.tokenize(chunk.title + " " + chunk.text)
            # Term frequencies
            tf = {}
            for tok in chunk.tokens:
                tf[tok] = tf.get(tok, 0) + 1
            chunk.tf = tf
            chunk.dense_vector = self._generate_dense_embedding(chunk.title + " " + chunk.text)
            self.chunks.append(chunk)

        self.rebuild_index()

    def clear(self):
        self.chunks = []
        self.doc_freq = {}
        self.total_docs = 0
        self.is_indexed = False

    def rebuild_index(self):
        """Calculates global inverse document frequencies (IDF)."""
        self.doc_freq = {}
        self.total_docs = len(self.chunks)

        for chunk in self.chunks:
            unique_tokens = set(chunk.tokens)
            for tok in unique_tokens:
                self.doc_freq[tok] = self.doc_freq.get(tok, 0) + 1

        self.is_indexed = True

    def search(self, query: str, top_k: int = 5, clearance_level: int = 4) -> List[Tuple[Chunk, float, Dict[str, float]]]:
        """
        Executes hybrid semantic + lexical search over the vector index.
        Returns top matching chunks with similarity score breakdown.
        """
        if not self.chunks or not query.strip():
            return []

        query_tokens = self.tokenize(query)
        query_dense = self._generate_dense_embedding(query)
        query_tf = {}
        for t in query_tokens:
            query_tf[t] = query_tf.get(t, 0) + 1

        results = []
        N = max(1, self.total_docs)

        for chunk in self.chunks:
            # 1. Lexical BM25 / TF-IDF Similarity
            lexical_score = 0.0
            for q_tok, q_count in query_tf.items():
                if q_tok in chunk.tf:
                    tf_val = chunk.tf[q_tok] / len(chunk.tokens)
                    df_val = self.doc_freq.get(q_tok, 1)
                    idf_val = math.log(1 + (N - df_val + 0.5) / (df_val + 0.5))
                    lexical_score += tf_val * idf_val * q_count

            # Normalize lexical score
            lexical_score = min(1.0, lexical_score * 3.0)

            # 2. Dense Cosine Similarity
            dense_dot = sum(q * c for q, c in zip(query_dense, chunk.dense_vector))
            dense_score = max(0.0, min(1.0, (dense_dot + 1.0) / 2.0))

            # 3. Hybrid Combination Score
            hybrid_score = (self.hybrid_alpha * dense_score) + ((1.0 - self.hybrid_alpha) * lexical_score)

            # Direct token match boost (e.g. searching exact secret key names or IP addresses)
            exact_matches = set(query_tokens).intersection(set(chunk.tokens))
            if exact_matches:
                hybrid_score = min(1.0, hybrid_score + 0.15 * len(exact_matches))

            score_details = {
                "hybrid_score": round(hybrid_score, 4),
                "dense_score": round(dense_score, 4),
                "lexical_score": round(lexical_score, 4),
                "exact_matches": list(exact_matches)
            }

            results.append((chunk, hybrid_score, score_details))

        # Sort descending by hybrid score
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
