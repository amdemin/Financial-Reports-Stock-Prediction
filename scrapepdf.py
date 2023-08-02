import pdfplumber
import os
import re
import sys
import traceback
from tqdm import tqdm


# Define headings in the document using word size function
def word_ratio_func(word):
    try:
        word_length = len(word["text"])
        word_bottom = float(word['bottom'])
        word_top = float(word['top'])
        return (word_bottom - word_top), word_length, word["text"]
        
    except:
        return 0, 0, 0
    

# get file paths for all pdfs (does not work for pdfs in subdirectories)
# def get_file_paths(directory):
    
#     file_paths = []
#     for root, directories, files in os.walk(directory):
#         for filename in files:
#             filepath = os.path.join(root, filename)
#             file_paths.append(filepath)
#     return file_paths
    

# Preprocess the text
def preprocess_text(texts):

    # preprocess the text
    text = "".join(texts.values()).strip("●").strip("*")
    text = text.split("\n")
    text = [x for x in text if x != '' and x.startswith("Source") == False]
    text = [x[0].replace("●", "") + x[1:] if x[0] == "●" else x for x in text]
    text = [x[0].replace("*", "") + x[1:] if x[0] == "*" else x for x in text]
    text = [x[0].replace("○", "") + x[1:] if x[0] == "○" else x for x in text]
    text = [x[0].replace("1", "") + x[1:] if x[1:3] in ["Q1", "Q2", "Q3", "Q4"] else x for x in text]
    text = text[2:]

    return text

# Scrape the text from the pdf file
def scrape_pdf(pdf_paths):
    
    # store the pdf text and headings in dictionaries
    pdf_texts = {}
    pdf_headings = {}

    # iterate over the pdf files
    for file_path in tqdm(pdf_paths):

        try:
            
            # open the pdf file using pdfplumber library
            reader = pdfplumber.open(file_path)

            # store the text and headings within one pdf file
            texts = {}
            headings = []
            headings_count = 0

            for page_number in range(0, len(reader.pages)):

                # get the specific page from the pdf file
                page = reader.pages[page_number]
                # extract text from page
                text = page.extract_text()
                # add text to dictionary
                texts[page_number] = text

                # extract headings from page
                words = page.extract_words()
                word_count = 0
                while word_count < len(words):
                    # find if the words are large enough to be headings
                    word_size, word_length, word_text = word_ratio_func(words[word_count])
                    heading = []

                    if word_size > 15 and word_length > 1:
                        while True:
                            heading.append(word_text)
                            word_count += 1
                            if word_count >= len(words):
                                break
                            word_size, word_length, word_text = word_ratio_func(words[word_count])
                            if not word_size > 15 and word_length > 1:
                                headings.append(" ".join(heading))
                                word_count += 10
                                break
                    headings_count += 1
                    word_count += 1
                
                # break if the page covers the reference section
                if re.search("\nReference\n", text):
                    break
            
            # preprocess the text
            text = preprocess_text(texts)
            final_text = " ".join(text)

            # export the text to a txt file
            with open("Txt/" + file_path.split("/")[-1].split(".")[0] + ".txt", "w", encoding='utf-8') as f:
                f.write(final_text)

            # add the text to the dictionary
            pdf_texts[file_path.split("/")[-1].split(".")[0]] = final_text
            # add the headings to the dictionary
            pdf_headings[file_path.split("/")[-1].split(".")[0]] = headings

        except Exception as e:

            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)

            filename = traceback_details[-1][0]
            line_no = traceback_details[-1][1]
            func = traceback_details[-1][2]

            print(f"Exception occurred in file {filename} at line {line_no} in function {func}")
            print(f"Exception type: {exc_type.__name__}, Exception message: {str(e)}")

            continue

    # export the text to a txt file
    with open("Txt/" + file_path.split("/")[-1].split(".")[0] + ".txt", "w", encoding='utf-8') as f:
        f.write(final_text)
    
    return pdf_texts, pdf_headings