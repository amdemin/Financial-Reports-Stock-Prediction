# Load libraries
from tqdm.notebook import tqdm
import spacy
import pandas as pd
import numpy as np
from transformers import pipeline
import os
import pickle
import time


def tokenize_reports(pdf_texts):
    
    # Initialize a dictionary to store the joined sentences for each report.
    joined_sentences = {}

    # Iterate over each report in pdf_texts.
    for report_name, report_text in pdf_texts.items():

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


def calculate_baseline_keyword_polarity(joined_sentences, keywords):

    # Initialize the sentiment analysis pipeline
    sentiment_analysis = pipeline("sentiment-analysis")

    # Initialize a dictionary to store the sentences and their sentiment scores for each report
    sentiment_results_dict = {}

    # Iterate over each report
    for report_name, sentences in tqdm(joined_sentences.items()):

        # Initialize a dictionary to store the sentiment analysis results for the current report
        report_sentiment_results = {keyword: [] for keyword in keywords}

        for sentence in sentences:
            if len(sentence) < 512: 
                for keyword in keywords:
                    if keyword in sentence.lower():
                        # Analyze the sentiment of the sentence
                        sentiment_result = sentiment_analysis(sentence)[0]
                        report_sentiment_results[keyword].append(sentiment_result)

        # Add the results to the dictionary
        sentiment_results_dict[report_name] = report_sentiment_results

    return sentiment_results_dict



if __name__ == "__main__":

    last_report = True
    if last_report:
        # Load the latest pdf text from the pickle file
        pdf_texts = pickle.load(open("Src/pdf_texts_last_report.pkl", "rb"))
    else:
        # Load 50 pdf texts from the pickle file
        pdf_texts = pickle.load(open("Src/pdf_texts.pkl", "rb"))

    # Load nlp model
    nlp = spacy.load("en_core_web_sm")

    start = time.time()

    # Tokenize the reports
    joined_sentences = tokenize_reports(pdf_texts)
    # Define keywords
    keywords = ['revenue', 'forecast', 'profit']
    # Analyze the sentiment of the sentences containing the keywords
    baseline_keyword_polarity_dict = calculate_baseline_keyword_polarity(joined_sentences, keywords)

    end = time.time()
    print('Time taken to calculate sentiment using baseline keyword model: ', end - start)

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
    
    print(baseline_keyword_polarity_df.head())

    # export dataframe to csv
    # baseline_keyword_polarity_df.to_csv('Scores/baseline_keyword_polarity.csv', index=False)