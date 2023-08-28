# ARP

### The code is organized as follows:
1. 'module_process_pdf.py' is file that transforms the pdf files into text files
2. 'module_text_blocks.py' is file that processes the text files into blocks of text based on headings, convenient for analysis
3. 'module_sentiment_"ModelName".py' are files containing models that perform sentiment analysis individually
4. 'notebook_dataset_analysis.ipynb' is file that visualises our cleaned data 
5. 'notebook_evaluation.ipynb' is file that evaluates all the models
6. 'notebook_pipeline.ipynb' is file that runs the whole sentiment pipeline for a specific document



### Folders:
- Scores (contain sentiment scores of relevant models)
- Shareholder letters (contain letters in the .pdf format)
- Txt (contain shareholder letters in the .txt format)
- Src (contain other extra files for data analysis, such as pickle, csv files)

### Libraries to install before usage:

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

**Amazon, Google and OpenAI API keys are needed to run the models**

### Amazon

`AWS_ACCESS_KEY_ID = "YOUR_ACCESS_KEY_ID"` <br>
`AWS_SECRET_ACCESS_KEY = "YOUR_SECRET_ACCESS_KEY"` <br>
`AWS_REGION = "YOUR_REGION"`

### Google

`{` <br>
  `"client_id": "YOUR_CLIENT_ID"`, <br>
  `"client_secret": "YOUR_CLIENT_SECRET",` <br>
  `"quota_project_id": "YOUR_QUOTA_PROJECT_ID",` <br>
  `"refresh_token": "YOUR_REFRESH_TOKEN",` <br>
  `"type": "authorized_user"` <br>
`}`

### OpenAI

`openai_api_key = "YOUR_OPENAI_API_KEY"`