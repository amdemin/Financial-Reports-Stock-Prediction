# Load libraries
import pandas as pd
import numpy as np
import spacy
import pickle
from tqdm.notebook import tqdm
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer, RobertaTokenizer, RobertaForSequenceClassification
import torch
from torch.nn.functional import softmax


def tokenize_reports(pdf_texts):
    
    # Initialize a dictionary to store the joined sentences for each report.
    joined_sentences = {}

    # Iterate over each report in pdf_texts.
    for report_name, report_text in tqdm(pdf_texts.items()): # 18 seconds

        # Split the report text into sentences.
        sentences = nlp(report_text).sents

        # Initialize a list to hold the tokenized sentences for this report.
        tokenized_report_sentences = []

        # Iterate over each sentence.
        for sentence in sentences:
            # Tokenize, lemmatize, and remove stop words and punctuation.
            tokenized = [token.lemma_ for token in sentence if not token.is_stop and not token.is_punct]
            # Add the tokenized sentence to the list.
            tokenized_report_sentences.append(tokenized)

        # Join each tokenized sentence into a single string, and store them in a list.
        joined_report_sentences = [' '.join(sentence) for sentence in tokenized_report_sentences]

        # Add the joined sentences for this report to joined_sentences.
        joined_sentences[report_name] = joined_report_sentences 

    return joined_sentences


def calculate_roberta_polarity(joined_sentences, keywords):
      
    # Initialize a dictionary to store the sentences and their sentiment scores for each report
    sentiment_results_dict = {}

    # Iterate over each report
    for report_name, sentences in joined_sentences.items():
        # Initialize a dictionary to store the sentiment analysis results for the current report
        report_sentiment_results = {keyword: [] for keyword in keywords}

        # Create a list to hold sentence chunks
        sentence_chunks = []

        for sentence in sentences:
            # If a sentence exceeds 512 tokens, break it into chunks
            if len(sentence) >= 512:
                chunked_sentences = [sentence[i:i + 512] for i in range(0, len(sentence), 512)]
                sentence_chunks.extend(chunked_sentences)
            else:
                sentence_chunks.append(sentence)

        # Analyze the sentiment for each sentence chunk using BERT model
        for chunk in sentence_chunks:
            chunk_lower = chunk.lower()
            for keyword in keywords:
                if keyword in chunk_lower:
                    inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True, max_length=512)
                    outputs = model(**inputs)
                    probs = softmax(outputs.logits, dim=1)
                    sentiment_result = {
                        "label": "positive" if probs[0][1] > probs[0][0] else "negative",
                        "score": probs[0][1].item()
                    }
                    report_sentiment_results[keyword].append(sentiment_result)

        # Add the results to the dictionary
        sentiment_results_dict[report_name] = report_sentiment_results

    return sentiment_results_dict


if __name__ == "__main__":


    # Load the pre-trained BERT model and tokenizer
    model_name = "roberta-base"
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForSequenceClassification.from_pretrained(model_name)

    # Load nlp model
    nlp = spacy.load("en_core_web_sm")

    # Load pdf texts from the pickle file
    # pdf_texts = pickle.load(open("Src/pdf_texts.pkl", "rb"))
    pdf_texts = pickle.load(open("PipelineFiles/pdf_texts.pickle", "rb"))

    # Tokenize the reports
    joined_sentences = tokenize_reports(pdf_texts)
    
    # Define keywords
    keywords = ['revenue', 'forecast', 'profit']
    # Analyze the sentiment of the sentences containing the keywords
    baseline_keyword_polarity_dict = calculate_roberta_polarity(joined_sentences, keywords)

    # Initialize a dictionary to hold total scores for each keyword in each report
    total_scores = {report: {keyword: 0 for keyword in keywords} for report in baseline_keyword_polarity_dict.keys()}

    # Calculate total scores for each keyword in each report
    for report_name, keywords_dict in baseline_keyword_polarity_dict.items():
        for keyword, sentiments in keywords_dict.items():
            for sentiment in sentiments:
                # If the sentiment is POSITIVE, add the score
                # If the sentiment is NEGATIVE, subtract the score
                if sentiment['label'] == 'POSITIVE':
                    total_scores[report_name][keyword] += sentiment['score']
                else:
                    total_scores[report_name][keyword] -= sentiment['score']

    # Convert the total_scores to a DataFrame
    baseline_keyword_polarity_df = pd.DataFrame(total_scores).T
    baseline_keyword_polarity_df.reset_index(inplace=True)
    baseline_keyword_polarity_df.columns = ['pdf_name', 'revenue_score', 'forecast_score', 'profit_score']
    baseline_keyword_polarity_df['polarity'] = baseline_keyword_polarity_df['revenue_score'] + baseline_keyword_polarity_df['forecast_score'] + baseline_keyword_polarity_df['profit_score']
    
    # print(baseline_keyword_polarity_df.head())

    # export dataframe to csv
    # baseline_keyword_polarity_df.to_csv('Scores/baseline_keyword_polarity.csv', index=False)