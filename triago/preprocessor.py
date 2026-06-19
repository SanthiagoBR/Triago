import re
from collections import Counter
from typing import Iterable

DEFAULT_STOP_WORDS = {
    "de", "do", "da", "dos", "das", "e", "o", "a", "os", "as", "um", "uma",
    "para", "por", "com", "sem", "no", "na", "nos", "nas", "em", "que", "se",
    "ao", "à", "às", "este", "esta", "esses", "essas", "isso",
    "é", "não", "nao", "foi", "ser", "são", "ja", "já", "mais", "mas", "tambem",
    "também", "como", "pelo", "pela", "pelos", "pelas", "me", "minha",
}
TOKEN_PATTERN = re.compile(r"\b[\wáàâãéèêíïóôõöúüçÁÀÂÃÉÈÊÍÏÓÔÕÖÚÜÇ-]+\b", flags=re.UNICODE)


class Preprocessor:
    def __init__(self, stop_words: Iterable[str] = None):
        self.stop_words = set(word.lower() for word in (stop_words or DEFAULT_STOP_WORDS))

    def tokenize(self, text: str):
        if not text:
            return []
        text = text.lower()
        tokens = TOKEN_PATTERN.findall(text)
        return [token for token in tokens if token not in self.stop_words]

    def text_to_token_counts(self, text: str):
        tokens = self.tokenize(text)
        return Counter(tokens)
