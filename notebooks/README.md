# Overview

## Introduction

I compared several supervised and unsupervised machine learning techniques to address the challenge of extracting the top desired job skills under the
Data Science category. My proposed approaches aim to identify new and emerging skills that have not been seen before. I trained various model on text
corpuses which I scraped for 3 different online job portals.

### Data Acquisition

I acquired my data by scraping job postings from various sources that were categorized under Data Science. In total, I was able to web-scrape 221 job
posts. The data was contained within the descriptions of each post. I then compiled the data into a MongoDB database for further analysis. After creating
this dataset, I randomly extracted 4000 noun phrase samples, which I manually labeled as not_skill, hard_skill, or soft_skill. This was a hard task as some
sentences are too ambiguous to label. An important observation here is that the complete dataset is not balanced, as the amount of soft_skills is small.

## Models

### Supervised Learning Classifiers

I used a variety of simple supervised learning classifiers, in order to classify the training dataset into 3 categories: not_skill, hard_skill, soft_skill.
The classifiers I tested are the following:

1. Multinomial Naive Bayes
2. Support Vector Machine
3. Linear Support Vector Machine
4. Random Forest
5. Logistic Regression

After extensive testing and hyperparameter-tuning, all classifiers yielded similar scores, with two being the clear winners, `LinearSVC` and `MultinomialNB`.

### Word2Vec

`Word2vec` is a family of self-learning algorithms that let us learn and train word embeddings from a corpus. One way of learning vector represantation
of words is called *continuous skip-gram model*. This model predicts the words around the word currently being searched. The amount of words to be
searched has a certain range which we specify.

Word2Vec was able to identify some useful skills such as *julia, kotlin, r,* etc. lthough the extracted keywords were useful and representative of the Data
Science domain, the model also extracted a lot of noise, which makes it difficult to separate soft and hard skills, thus making the model's results undesirable.
Improving Word2Vec accuracy can be achieved by providing a larger dataset of job post descriptions.

### Deep Learning Models

Moving on to more complex models called deep learning models, I used `word embeddings` in combination with various deep learning layers. `Word embeddings` are
a way of representing words as dense vectors of real numbers. They are used in natural language processing (NLP) to encode words in a way that allows them to
be used as input to machine learning models.

The main advantage of word embeddings is that they allow us to use an efficient, dense representation in which similar words have a similar encoding. This makes
it possible to use machine learning algorithms to analyze text data and perform tasks such as sentiment analysis, text classification, and machine translation.

#### Word Embeddings + Convolutions

In text classification models, convolutions are used to recognize topics and relationships between words. It is a feature transformation that groups a set of
sequential data into a convoluted, compressed data. In general, convolutions of one dimention takes care of neighboring words by using a filter length that
implies a context window of words.

This model overfited the data, as the training set accuracy is higher than the validation set accuracy and the loss is also increasing. However, it was able to
extract useful skills from the job descriptions.

#### Word Embeddings + LSTM

`LSTM` stands for Long Short-Term Memory and is a type of recurrent neural network (RNN) that is capable of learning long-term dependencies. In general, LSTM
layers are used in sequence prediction problems where there is a need to remember information from earlier parts of the sequence. In this model, the LSTM layer
takes in the output of the embedding layer and processes it sequentially.

This model behaves the best of all models so far. Another observation we can make is that this simple model slightly overfitted the data. It exctracted the
most relevant nouns for both the hard_skills and soft_skills categories.

## Results

| Model                         | Type            | Test Accuracy | Notes                                             |
| ----------------------------- | --------------- | ------------- | ------------------------------------------------- |
| Linear Support Vector Machine | Supervised      | 0.8215        | **Very good** results. Minimal noise extracted.   |
| Word2Vec                      | Self-Supervised | N/A           | **Poor** results. Lot's of noise extracted.       |
| Word Embedding + Convolutions | Supervised      | 0.8205        | **Good** results. Overfitted the data.            |
| Word Embedding + LSTM         | Supervised      | 0.8329        | **Best** results so far. Minimal noise extracted. |

## Future Work

Many of the job descriptions are represented by verb phrases. In that case we would have to create a new training dataset from verb phrases and train new models.
The Word Embeddings + LSTM model also has a very small amount of noise extracted which is desirable. Future work can be to generalize models to verb phrase and
not only noun sequences. In addition, a classifier using the popular BERT embeddings woould be a nice addition. Lastly this work focused only on word embeddings
thus another approach yet to be explored would be sentence embeddings.
