# app/adapters/offline.py — adapters for running the reference system offline (7.1)
#
# Not production adapters: they exist so the whole system — every port,
# handler, graph and wrapper — can run on a laptop with no API key and no
# Docker. They prove the same point as the fakes, at full scale: the core
# does not know or care what sits behind its ports.
import hashlib
import math
import re

from app.ports import EmbeddingPort, LLMPort

_WORD = re.compile(r"[a-zà-ÿ0-9]+")


def _words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


class HashingEmbeddings(EmbeddingPort):
    """Bag-of-words feature hashing: texts that share words get similar vectors."""

    def __init__(self, dimensions: int = 256) -> None:
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        for word in _words(text):
            bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % self._dimensions
            vector[bucket] += 1.0
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


class ExtractiveLLM(LLMPort):
    """Answers by quoting the context sentence that best overlaps the question.
    Handles the routing and rewriting prompts Part V's graphs send."""

    def complete(self, prompt: str) -> str:
        if prompt.startswith("Context:") and "\n\nQuestion:" in prompt:
            context, question = prompt.removeprefix("Context:").split("\n\nQuestion:", 1)
            return self._best_sentence(context, question)
        if "comparative" in prompt:
            return "yes" if re.search(r"\b(compare|versus|vs|difference)\b", prompt.lower()) else "no"
        if "Rewrite this question" in prompt:
            return prompt.rsplit("\n\n", 1)[-1]
        if "database count, or both" in prompt:
            return "a database count" if re.search(r"\bhow many\b", prompt.lower()) else "document search"
        if prompt.startswith("You write one SQL SELECT"):
            return "SELECT COUNT(*) AS documents FROM documents"
        if "Rows returned by the database:" in prompt:
            rows = prompt.split("Rows returned by the database:", 1)[1].split("\n")[0].strip()
            return f"The database returned: {rows}"
        return prompt[:200]

    @staticmethod
    def _best_sentence(context: str, question: str) -> str:
        # Split into sentences, remembering the most recent markdown heading so
        # "2023" in "# Travel Policy 2023" still counts for the sentences below it.
        sentences: list[tuple[str, set[str]]] = []
        heading: set[str] = set()
        for line in context.splitlines():
            line = line.strip()
            if line.startswith("#"):
                heading = set(_words(line))
                continue
            for sentence in re.split(r"(?<=[.!?])\s+", line):
                if sentence:
                    sentences.append((sentence, heading))
        if not sentences:
            return ""
        wanted = set(_words(question)) - _STOPWORDS
        # Rare words matter more than common ones (a tiny IDF).
        df: dict[str, int] = {}
        for sentence, _ in sentences:
            for w in set(_words(sentence)):
                df[w] = df.get(w, 0) + 1

        def score(item: tuple[str, set[str]]) -> float:
            sentence, head = item
            words = set(_words(sentence))
            body = sum(1.0 / df.get(w, 1) for w in wanted & words)
            return body + 0.5 * len(wanted & (head - words))

        return max(sentences, key=score)[0]


_STOPWORDS = {
    "a", "an", "and", "are", "can", "do", "does", "for", "how", "i", "in", "is", "it", "much", "of", "on",
    "or", "the", "to", "what", "when", "where", "which", "who", "with",
}
