# Import libraries
import pandas as pd
import numpy as np
import re

# Split the text into blocks based on the headings
def split_text_into_blocks(text, headings):

    # define dictionary for storing text blocks
    text_blocks = {}

    # Iterate over the headings
    for heading in range(len(headings)):

        # in the beginning of document, there is no heading, so let's define it as document intro
        if heading == 0:
            document_intro = text.split(headings[heading])[0]
            text_blocks['Document_intro'] = document_intro
        
        # prevent the error of index out of range
        if len(text.split(headings[heading])) > 1:
            text_after_heading = text.split(headings[heading])[1]
        else:
            text_after_heading = ""
        
        # identify the last heading
        if heading == len(headings) - 1:
            text_blocks[headings[heading]] = text_after_heading
            break
        else:
            # identify middle headings
            text_of_heading = text_after_heading.split(headings[heading+1])[0]
            text_blocks[headings[heading]] = text_of_heading
    
    return text_blocks


# Clean the text blocks
def clean_text_blocks(text_blocks):

    # iterate over text blocks, removing '\u200b' and extra spaces
    for key in text_blocks:
        text_blocks[key] = re.sub('\u200b', '', text_blocks[key])
        text_blocks[key] = re.sub(' +', ' ', text_blocks[key])

    return text_blocks