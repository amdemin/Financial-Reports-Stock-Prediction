# ARP

### Please, before trying the code familiarise yourself with our project structure

### Folders:
1. Pipeline (contain main preprocessing modules)
- 'module_scrape_pdf.py' extracts and downloads pdf files from the website
- 'module_process_pdf.py' transforms pdf files into text files
- 'module_text_blocks.py' splits text files into blocks of text based on headings, convenient for further analysis
- 'module_functions.py' normalises the model sentiment scores
2. Models              (contain sentiment models modules)
- 'module_sentiment_"model_name".py' contain model that perform sentiment analysis
3. Scores              (contain sentiment scores of relevant models)
4. Shareholder letters (contain letters in the .pdf format)
5. Src                 (contain other extra files for data analysis, such as pickle, csv files)
6. PostMarket          (contain notebooks to scrape and calculate sentiment of Financial Times articles)

### Main Notebooks
1. 'Notebook_Dataset_Analysis.ipynb' analyses and visualises our preprocessd data 
2. 'Notebook_Evaluation.ipynb' evaluates all the models
3. 'Notebook_Pipeline.ipynb' runs the whole sentiment pipeline for a specific document / documents


### Libraries to install before usage (Python Version==3.10):

* `pip install selenium==4.11.2` 
* `pip install webdriver_manager`
* `pip install pdfplumber`
* `pip install pymupdf`
* `pip install google-cloud`
* `pip install openai`
* `pip install boto3`
* `pip install textblob`
* `pip install tqdm`
* `pip install nltk`
* `pip install wordcloud`
* `pip install scikit-learn`
* `pip install transformers`
* `pip install spacy` and `python -m spacy download en_core_web_sm`

**Amazon, Google and OpenAI API keys are needed to run their models**

### Amazon (name the file as *credentials_amazon.py*)

`AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID"` <br>
`AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY"` <br>
`AWS_REGION = "YOUR_REGION"`

### Google (name the file as *credentials_google.json*)

`{` <br>
  `"client_id": "YOUR_CLIENT_ID"`, <br>
  `"client_secret": "YOUR_CLIENT_SECRET",` <br>
  `"quota_project_id": "YOUR_QUOTA_PROJECT_ID",` <br>
  `"refresh_token": "YOUR_REFRESH_TOKEN",` <br>
  `"type": "authorized_user"` <br>
`}`

### OpenAI (name the file as *credentials_openai.py*)

`openai_api_key = "YOUR_OPENAI_API_KEY"`