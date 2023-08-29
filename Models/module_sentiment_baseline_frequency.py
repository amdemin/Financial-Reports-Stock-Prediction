# Load libraries
import pandas as pd
import pickle
import time
import os

def calculate_baseline_frequency_polarity(lexicon_path, text):

    try:
        
        # Loading the Loughran and McDonald (LM) Lexicon CSV file
        lm_lexicon = pd.read_csv(lexicon_path)

        # Extracting positive and negative words from the LM Lexicon
        positive_words_lm = lm_lexicon[lm_lexicon['Positive'] > 0]['Word'].str.lower().tolist()
        negative_words_lm = lm_lexicon[lm_lexicon['Negative'] > 0]['Word'].str.lower().tolist()

        # Calculating the baseline frequency polarity
        words = text.lower().split()
    
        # Counting occurrences of positive and negative words
        positive_count = sum(word in positive_words_lm for word in words)
        negative_count = sum(word in negative_words_lm for word in words)
    
        # Calculating sentiment score as the difference between positive and negative counts
        sentiment_score = positive_count - negative_count
    
        return sentiment_score

    except Exception as e:

        print('Error in loading the LM Lexicon: ', e)


if __name__ == "__main__":

    last_report = True
    if last_report:
        # Load the latest pdf text from the pickle file
        pdf_texts = pickle.load(open("Src/pdf_texts_last_report.pkl", "rb"))
    else:
        # Load 50 pdf texts from the pickle file
        pdf_texts = pickle.load(open("Src/pdf_texts.pkl", "rb"))

    # set start time
    start = time.time()

    # Calculate the baseline frequency polarity for each report
    lexicon_path = 'Src/Loughran-McDonald_MasterDictionary_1993-2021.csv'
    baseline_frequency_polarity = {report_name: calculate_baseline_frequency_polarity(lexicon_path, text) for report_name, text in pdf_texts.items()}

    # set end time
    end = time.time()
    print('Time taken to calculate sentiment using baseline frequency model: ', end - start)

    # convert dictionary to dataframe
    baseline_frequency_polarity_df = pd.DataFrame.from_dict(baseline_frequency_polarity, orient='index', columns=['polarity']).reset_index()
    baseline_frequency_polarity_df.rename(columns={'index': 'pdf_name'}, inplace=True)

    # export dataframe to csv
    # baseline_frequency_polarity_df.to_csv('Scores/baseline_frequency_polarity.csv', index=False)