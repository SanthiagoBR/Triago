import math
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Sequence

from .preprocessor import Preprocessor


class NaiveBayesClassifier:
    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self.preprocessor = Preprocessor()
        self.class_counts: Counter[str] = Counter()
        self.word_counts: Dict[str, Counter[str]] = defaultdict(Counter)
        self.class_word_totals: Counter[str] = Counter()
        self.vocabulary: set[str] = set()
        self.total_documents = 0

    def fit(self, documents: Sequence[str], labels: Sequence[str]):
        if len(documents) != len(labels):
            raise ValueError("Documents and labels must have the same length")
        for document, label in zip(documents, labels):
            self.total_documents += 1
            self.class_counts[label] += 1
            token_counts = self.preprocessor.text_to_token_counts(document)
            self.word_counts[label].update(token_counts)
            self.class_word_totals[label] += sum(token_counts.values())
            self.vocabulary.update(token_counts.keys())

    def _log_prior(self, label: str) -> float:
        return math.log(self.class_counts[label] / self.total_documents)

    def _log_likelihood(self, word: str, label: str) -> float:
        word_count = self.word_counts[label].get(word, 0)
        vocabulary_size = max(1, len(self.vocabulary))
        numerator = word_count + self.alpha
        denominator = self.class_word_totals[label] + self.alpha * vocabulary_size
        return math.log(numerator / denominator)

    def predict_log_proba(self, text: str) -> Dict[str, float]:
        if not self.class_counts:
            raise ValueError("The classifier has not been trained yet")
        token_counts = self.preprocessor.text_to_token_counts(text)
        scores: Dict[str, float] = {}
        for label in self.class_counts:
            score = self._log_prior(label)
            for word, count in token_counts.items():
                score += self._log_likelihood(word, label) * count
            scores[label] = score
        return scores

    def predict_proba(self, text: str) -> Dict[str, float]:
        scores = self.predict_log_proba(text)
        max_score = max(scores.values())
        exp_scores = {label: math.exp(score - max_score) for label, score in scores.items()}
        total = sum(exp_scores.values())
        return {label: prob / total for label, prob in exp_scores.items()}

    def predict(self, text: str) -> str:
        probabilities = self.predict_log_proba(text)
        return max(probabilities, key=probabilities.get)
