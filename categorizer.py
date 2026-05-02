import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


df = pd.read_csv('malaysian_nlp_dataset.csv')

X_train, y_train = df['Item'], df['Category']

# Vectorizer and Classifier
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)

clf = MultinomialNB()
clf.fit(X_train_vec, y_train)

def categorize_expense(description: str) -> str:
    """
    Categorize expense description into categories like Food, Transport, etc.
    """
    vec = vectorizer.transform([description])
    return clf.predict(vec)[0]