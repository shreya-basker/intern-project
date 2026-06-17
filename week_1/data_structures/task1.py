import re  # regular expressions
from collections import Counter


def word_counter(string1):
    words = re.findall(r"\b[a-zA-Z]+\b", string1.lower())
    counts = Counter(words)
    return counts.most_common(5)


def main():
    text = """Hello world! Hello everyone.
    This is the python programming world. Pyrhon. Python"""
    print(word_counter(text))
