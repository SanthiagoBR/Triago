import re
import unicodedata
from collections import Counter
from typing import Iterable

DEFAULT_STOP_WORDS = {
    "de", "do", "da", "dos", "das", "e", "o", "a", "os", "as", "um", "uma",
    "para", "por", "com", "sem", "no", "na", "nos", "nas", "em", "que", "se",
    "ao", "a", "as", "este", "esta", "estao", "esses", "essas", "isso",
    "e", "nao", "foi", "ser", "sao", "ja", "mais", "mas", "tambem",
    "como", "pelo", "pela", "pelos", "pelas", "me", "minha",
}
TOKEN_PATTERN = re.compile(r"\b[\w-]+\b", flags=re.UNICODE)


def strip_accents(text: str) -> str:
    """Remove diacríticos para unificar grafias (ex.: 'está' -> 'esta')."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


class Preprocessor:
    def __init__(self, stop_words: Iterable[str] = None):
        self.stop_words = {strip_accents(word.lower()) for word in (stop_words or DEFAULT_STOP_WORDS)}

    def tokenize(self, text: str):
        if not text:
            return []
        text = strip_accents(text.lower())
        tokens = TOKEN_PATTERN.findall(text)
        return [token for token in tokens if token not in self.stop_words]

    def text_to_token_counts(self, text: str):
        tokens = self.tokenize(text)
        return Counter(tokens)
