import pandas as pd
import re
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import warnings
from bs4 import MarkupResemblesLocatorWarning
from exploit_probability import calculate_exploit_probability
from vulnerability_classifier import classify_vulnerabilities

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Download NLTK resources
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)


# ==============================
# File Handling Agent
# ==============================

class FileHandlingAgent:

    def load_file(self, file_path):

        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)

        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)

        else:
            raise ValueError("Unsupported file format")

        print("File loaded successfully")
        print("Dataset shape:", df.shape)

        return df


# ==============================
# Preprocessing Agent
# ==============================

class PreProcessingAgent:

    def preprocess(self, df):

        print("Initial dataset size:", df.shape)

        df.columns = df.columns.str.upper()

        df = df.dropna(subset=["DESCRIPTION"])

        if "CVE-ID" in df.columns:
            df = df.drop_duplicates(subset=["CVE-ID"])

        df = df.drop_duplicates(subset=["DESCRIPTION"])

        df = df.reset_index(drop=True)

        print("Dataset after preprocessing:", df.shape)

        return df


# ==============================
# NLP Cleaning Agent
# ==============================

class NLPCleaningAgent:

    def __init__(self):
        self.stop_words = set(stopwords.words("english"))

    def clean_text(self, text):

        if pd.isna(text):
            return ""

        try:
            text = BeautifulSoup(str(text), "html.parser").get_text()
        except:
            text = str(text)

        text = text.lower()
        text = re.sub(r"[^a-zA-Z\s]", "", text)

        words = text.split()
        words = [word for word in words if word not in self.stop_words]

        return " ".join(words)


# ==============================
# Tokenization Agent
# ==============================

class TokenizationAgent:

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()

    def tokenize(self, text):

        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(word) for word in tokens]

        return tokens


# ==============================
# Feature Extraction Agent
# ==============================

class FeatureExtractionAgent:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500)

    def extract_features(self, texts):

        tfidf_matrix = self.vectorizer.fit_transform(texts)

        feature_names = self.vectorizer.get_feature_names_out()

        tfidf_df = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=feature_names
        )

        return tfidf_df


# ==============================
# NLP Pipeline
# ==============================

class NLPProcessingPipeline:

    def __init__(self):

        self.file_agent = FileHandlingAgent()
        self.preprocess_agent = PreProcessingAgent()
        self.clean_agent = NLPCleaningAgent()
        self.token_agent = TokenizationAgent()
        self.feature_agent = FeatureExtractionAgent()

    def process(self, file_path):

        try:

            # Load dataset
            df = self.file_agent.load_file(file_path)

            if df is None:
                raise ValueError("Dataset could not be loaded")

            # Preprocess dataset
            df = self.preprocess_agent.preprocess(df)

            if "DESCRIPTION" not in df.columns:
                raise ValueError("DESCRIPTION column not found in dataset")

            # AI vulnerability classification
            from vulnerability_classifier import classify_vulnerabilities
            df = classify_vulnerabilities(df)

            # NLP cleaning
            df["clean_text"] = df["DESCRIPTION"].apply(self.clean_agent.clean_text)

            # Tokenization
            df["tokens"] = df["clean_text"].apply(self.token_agent.tokenize)

            # Convert tokens to text
            df["processed_text"] = df["tokens"].apply(lambda x: " ".join(x))

            # TF-IDF feature extraction
            tfidf_features = self.feature_agent.extract_features(df["processed_text"])

            final_df = pd.concat([df, tfidf_features], axis=1)

            # Exploit probability calculation
            from exploit_probability import calculate_exploit_probability
            final_df = calculate_exploit_probability(final_df)

            # Save processed dataset
            final_df.to_csv("processed_vulnerabilities.csv", index=False)

            print("Processing completed")

            return final_df

        except Exception as e:

            print("Pipeline Error:", str(e))
            raise e


# ==============================
# FastAPI Function
# ==============================

def run_nlp_pipeline(file_path):

    pipeline = NLPProcessingPipeline()

    result = pipeline.process(file_path)

    joblib.dump(pipeline, "nlp_processing_pipeline.joblib")

    return result