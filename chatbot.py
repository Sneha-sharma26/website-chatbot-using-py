"""
1. Loads the scraped website content (website_content.txt)
2. Splits it into small chunks (like paragraphs/sentences)
3. Given a user question, finds the chunks that best match the question's keywords
4. Returns the best-matching text as the "answer"
"""

import math
import re
import os

CONTENT_FILE = "website_content.txt"

CHUNK_DELIMITER = "\n<<<CHUNK>>>\n"

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "do", "does", "did",
    "what", "which", "who", "whom", "this", "that", "these", "those",
    "of", "in", "on", "at", "for", "to", "and", "or", "with", "about",
    "your", "you", "i", "it", "its", "provide", "have", "has", "can",
    "please", "tell", "me", "company", "there"
}

YES_NO_STARTERS = (
    "does", "do", "is", "are", "can", "could", "will", "would",
    "has", "have", "did",
)


def load_content(filepath: str = CONTENT_FILE) -> str:
    """Load the scraped website text from disk."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"'{filepath}' not found. Run `python scraper.py` first "
            f"to generate it."
        )
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def split_into_chunks(text: str) -> list[str]:
    chunks = [c.strip() for c in text.split(CHUNK_DELIMITER)]
    return [c for c in chunks if c]


def get_keywords(text: str) -> set[str]:
    # Extract lowercase keywords from text, ignoring stopwords/punctuation (mininmum length = 2)

    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) >= 2}


class WebsiteChatbot:
    def __init__(self, filepath: str = CONTENT_FILE):
        raw_text = load_content(filepath)
        self.chunks = split_into_chunks(raw_text)
        # Precompute keyword sets for every chunk 
        self.chunk_keywords = [get_keywords(chunk) for chunk in self.chunks]
        self.word_weight = self._compute_word_weights()

    def _compute_word_weights(self) -> dict:
        num_chunks = len(self.chunks)
        doc_frequency = {}
        for chunk_kw in self.chunk_keywords:
            for word in chunk_kw:
                doc_frequency[word] = doc_frequency.get(word, 0) + 1

        weights = {}
        for word, freq in doc_frequency.items():
            # +1s avoid division by zero / log(0); common IDF formula
            weights[word] = math.log((num_chunks + 1) / (freq + 1)) + 1
        return weights

    def _score_chunk(self, question_keywords: set, chunk_kw: set) -> float:
        """Sum the weights of every keyword shared between question and chunk."""
        shared = question_keywords & chunk_kw
        return sum(self.word_weight.get(word, 0) for word in shared)

    def answer(self, question: str, top_n: int = 3) -> str:
        """
        Compare the question's keywords against every chunk's keywords,
        weighted by how distinctive each word is. Return the chunk(s)
        with the highest weighted score.
        """
        question_keywords = get_keywords(question)

        if not question_keywords:
            return "Could you rephrase your question with a bit more detail?"

        scores = []
        for idx, chunk_kw in enumerate(self.chunk_keywords):
            score = self._score_chunk(question_keywords, chunk_kw)
            if score > 0:
                scores.append((score, idx))

        if not scores:
            return (
                "I couldn't find anything about that on the website. "
                "Try asking about services, cloud solutions, AI/ML, "
                "security, or automation."
            )

        # Sort by highest weighted score first
        scores.sort(reverse=True)
        best_indices = [idx for _, idx in scores[:top_n]]
        answer_text = "\n\n".join(self.chunks[i] for i in best_indices)

        first_word = question.strip().split()[0].lower().strip("?.,!")
        if first_word in YES_NO_STARTERS:
            answer_text = f"Yes — {answer_text}"

        return answer_text


if __name__ == "__main__":
    bot = WebsiteChatbot()
    print("Chatbot ready! Type 'quit' to exit.\n")
    while True:
        q = input("You: ")
        if q.lower() in ("quit", "exit"):
            break
        print("Bot:", bot.answer(q), "\n")