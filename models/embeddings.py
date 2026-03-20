import logging
from config.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts):
    if not texts:
        return []
    try:
        model = _get_model()
        cleaned = [t.replace("\n", " ").strip() for t in texts]
        return model.encode(cleaned, normalize_embeddings=True, show_progress_bar=False).tolist()
    except Exception as exc:
        raise RuntimeError(f"Embedding error: {exc}") from exc


def embed_query(query):
    return embed_texts([query])[0]
