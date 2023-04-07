# Skills Extractor From Job Posts

## Introduction

This project is a skills extractor portfolio project that consists of a scraper for scraping job
listings and various machine learning techniques for analyzing the descriptions. The goal of this
project is to extract the top soft and hard skills of all job posts. This project is important
because it can help job seekers identify the most important skills for a particular job and tailor
their resumes accordingly.

## Requirements and Installation

For your convenience there is a file named requirements which you can check, which holds the
information about all the required libraries. After making sure you have python up and running in
your machine, you can install all the requirements with `pip`, by using the following command:

```shell
pip install -r requirements.txt
```

After that step, if you want to rerun the whole application you should create a file named
`credentials.json` in the root diretory of the project. This file should contain the following
code:

```json
{
    "username": "your@email.com",
    "password": "yourPassword"
}
```

These should be your credentials of the LinkedIn webside, in order to use the scraper correctly.

## Usage

### Clone the repository and install dependencies

1. Clone the repository
2. Install the dependencies as explained in the documentation

### Set up MongoDB

1. Install MongoDB in your system
2. A Python class will take care of initializing the localhost database and the collection

### Scraping Process

1. Navigate to the "modeling" directory: `cd modeling`
2. Run the scraper: `python scraper.py`
3. After successful scraping of the websites, you are ready to move on to analysis.

### Run the Analysis

1. Navigate to the "notebooks" directory: `cd notebooks`
2. Run each desired notebook one by one
3. Notebook number 1 contains an already successful run of the notebook. If you want to run it in
your own machine, you have to run through the scraping process first.

(Optional) If you want to rerun the analysis on your own scraped data, please run notebook
number 2 as well. In this case a file named `noun_chunks.csv` will be create. You have to take
this file, rename it to `noun_chunks_classified.csv` and manually identify each row in that
file as "not_skill", "soft_skill", or "hard_skill".

### Classifiers

#### Simple Models

The third notebook contains code for running a set of simple classifiers. This includes the following:

* Multinomial Naive Bayes
* Support Vector Machine
* Linear Support Vector Machine
* Random Forest
* Logistic Regression

Additionally, it includes a brief analysis and several improvements to the classifiers such as
n-gram range selection, cross-validation, and hyperparameter tuning through `GridSearchCV`.

#### Word Embeddings Classifier

In notebook number four, I created a word embeddings classifier. Word embeddings are a way of representing
words as dense vectors of real numbers. They are used in natural language processing (NLP) to encode words
in a way that allows them to be used as input to machine learning models.

The main advantage of word embeddings is that they allow us to use an efficient, dense representation in
which similar words have a similar encoding. This makes it possible to use machine learning algorithms to
analyze text data and perform tasks such as sentiment analysis, text classification, and machine translation.
