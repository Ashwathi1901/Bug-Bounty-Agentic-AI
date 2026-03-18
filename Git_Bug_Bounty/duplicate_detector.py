from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class DuplicateDetector:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500)

    def check_duplicate(self, new_desc, new_class, existing_reports):

        existing_descs = [r["description"] for r in existing_reports]

        corpus = existing_descs + [new_desc]

        vectors = self.vectorizer.fit_transform(corpus)

        new_vector = vectors[-1]
        old_vectors = vectors[:-1]

        desc_sim = cosine_similarity(new_vector, old_vectors).max()

        class_sim = 0

        for r in existing_reports:
            if r.get("type") == new_class:
                class_sim = 1
                break

        final_score = (0.6 * desc_sim) + (0.4 * class_sim)

        return float(final_score)