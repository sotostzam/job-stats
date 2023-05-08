# Skill Extraction From Job Posts

## Introduction

This project is a skills extraction application that comprises a utility class for scraping job
posts and various machine learning techniques for in-depth analysis. The goal of the project
is to extract the top soft and hard skills that companies ask for in their job posts. It can
help job seekers identify the most important skills needed for the industry and tailor their
resumes accordingly.

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
3. Notebook number one contains an execution of the notebook. If you want to run it in
your own machine, you have to run through the scraping process first.

(Optional) If you want to rerun the analysis on your own scraped data, please run notebook
number 2 as well. In this case a file named `noun_chunks.csv` will be create. You have to take
this file, rename it to `noun_chunks_classified.csv` and manually identify each row in that
file as "not_skill", "soft_skill", or "hard_skill".

### Classifiers

#### Supervised Learning Models

The third notebook contains code for running a set of simple classifiers. This includes the following:

* Multinomial Naive Bayes
* Support Vector Machine
* Linear Support Vector Machine
* Random Forest
* Logistic Regression

Additionally, it includes a brief analysis and several improvements to the classifiers such as
n-gram range selection, cross-validation, and hyperparameter tuning through `GridSearchCV`.

#### Word2Vec

Word2vec is a family of self-supervised algorithms that let us learn and train word embeddings from a corpus. One way
of learning vector represantation of words is called `continuous skip-gram` model. This model predicts the words
around the word currently being searched. The amount of words to be searched has a certain range which we specify.

In this model the first thing is to generate the positive-skip grams for each word. Positive in the sense that
the neightborhood of the word includes words that appear within the specified range or window. After this we will
have to find also the negative sampling for skip-gram generation. These are the pairs of the current word and an
amount of words that do not appear within our specified window.

#### Word Embeddings + Convolutions

In notebook number five, I created a deep learning model that contains `word embeddings` and a `convolution` layer.
Word embeddings are a way of representing words as dense vectors of real numbers. They are used in natural language
processing (NLP) to encode words in a way that allows them to be used as input to machine learning models. The main
advantage of word embeddings is that they allow us to use an efficient, dense representation in which similar words
have a similar encoding. This makes it possible to use machine learning algorithms to analyze text data and perform
tasks such as sentiment analysis, text classification, and machine translation.

In text classification models, convolutions are used to recognize topics and relationships between words. It is a
feature transformation that groups a set of sequential data into a convoluted, compressed data. In general,
convolutions of one dimention takes care of neighboring words by using a filter length that implies a context window
of words.

#### Word Embeddings + LSTM

In the last notebook (number six), I created a deep learning model that combines `word embeddings` with a
`Long Short-Term Memory(LSTM)` layer. LSTM networks are a type of recurrent neural network (RNN) that are capable
of learning long-term dependencies in sequential data. In particular, LSTM networks can be used to model the sequential
nature of job posts and capture long-term dependencies between words.

Word embeddings can then be used to represent each word as a vector in a high-dimensional space, which can help
capture semantic relationships between words. By combining these two techniques, it is possible to improve the
accuracy of skill extraction from job posts by identifying relevant keywords and phrases that are indicative of
specific skills. This deep learning model proved to be the best performing one compared to the previous models.
