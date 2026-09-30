# -*- coding: utf-8 -*-
import os


os("python -m spacy download fr_core_news_sm")

import json
import spacy
from nltk.corpus import wordnet as wn

nlp = spacy.load("fr_core_news_sm")

def extract_subject(text):
   doc = nlp(text)
   candidates = []
   for token in doc:
    if token.pos_ == "NOUN" and token.dep_ == "nmod":
      candidates.append(token.text)

   return candidates



def generate_keywords(subject, max_keywords=5):
    keywords = set()
    # Cherche les concepts correspondant au mot
    synsets = wn.synsets(subject, lang="fra")
    for synset in synsets:
        for lemma in synset.lemmas(lang="fra"):
            word = lemma.name().replace("_", " ")
            if word.lower() != subject.lower():
                keywords.add(word)
        for hypernym in synset.hypernyms():
            for lemma in hypernym.lemmas(lang="fra"):
                word = lemma.name().replace("_", " ")
                if word.lower() != subject.lower():
                    keywords.add(word)
        for hyponym in synset.hyponyms():
            for lemma in hyponym.lemmas(lang="fra"):
                word = lemma.name().replace("_", " ")
                if word.lower() != subject.lower():
                    keywords.add(word)
    return list(keywords)[:max_keywords]


def analyze(text):
    subjects = extract_subject(text)
    # Aucun sujet trouvé
    if not subjects:
        return {
            "subject": None,
            "keywords": []
        }

    # Pour l'instant, on prend le premier candidat
    subject = subjects[0]
    # Génération dynamique des keywords
    keywords = generate_keywords(subject)
    return {
        "subject": subject,
        "keywords": keywords
    }

def concept_to_json():
    text = input("Décris ton besoin : ")
    result = analyze(text)
    filename = f"{result["subject"]}.json"
    with open(filename, "w", encoding="utf-8") as file:
      json.dump(result, file, ensure_ascii=False, indent=4)
    return