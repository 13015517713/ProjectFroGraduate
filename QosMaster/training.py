# from transformers import pipeline
from transformers import pipeline
classifier = pipeline('sentiment-analysis')
t = classifier('We are very happy to show you the 🤗 Transformers library.')
print(t)

