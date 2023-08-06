# Import libraries
import pandas as pd
import numpy as np
import re

# Split the text into blocks based on the headings
def split_text_into_blocks(text, headings):

    # Split the text into blocks based on the headings
    text_blocks = {}

    # Iterate over the headings
    for heading in range(len(headings)):

        if heading == 0:
            document_intro = text.split(headings[heading])[0]
            text_blocks['Document_intro'] = document_intro
        
        text_after_heading = text.split(headings[heading])[1]
        if heading == len(headings) - 1:
            text_blocks[headings[heading]] = text_after_heading
            break
        else:
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