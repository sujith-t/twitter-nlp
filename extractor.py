# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 16:26:51 2022

@author: sujith
"""

import pandas as pd
import re

from nltk import naivebayes
from nltk import classify
from sklearn import metrics
import numpy as np
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer

"""
Bag of words extraction
"""


def bag_of_words_extractor(texts, ngram_range=(1, 1)):
    count_vectorizor = CountVectorizer(min_df=1, ngram_range=ngram_range)
    features = count_vectorizor.fit_transform(texts)

    return count_vectorizor, features


"""
# Generate a summary of features
# produces a feature range and counts
"""


def feature_summary(features, feature_names, feature_range=100):
    df = pd.DataFrame(data=features, columns=feature_names)
    summary = pd.DataFrame(columns=["lower", "upper", "count"])

    for i, row in df.iterrows():
        num_features = sum(row)
        lower = (num_features // feature_range) * feature_range
        upper = ((num_features // feature_range) + 1) * feature_range

        tmp_df = summary.loc[(summary["lower"] == lower) & (summary["upper"] == upper)]

        if tmp_df.empty:
            collection = []
            tmp_data = [lower, upper, 1]
            collection.append(tmp_data)
            tmp_df = pd.DataFrame(collection, columns=["lower", "upper", "count"])
            summary = pd.concat([summary, tmp_df], ignore_index=True)
            summary.reset_index()
        else:
            inx = tmp_df.first_valid_index()
            summary.at[inx, 'count'] = summary.at[inx, 'count'] + 1

    summary = summary.sort_values(["lower", "upper"])

    print("News items per feature ranges distributions in %ds\n %s" % (feature_range, "-" * 50))

    for i, row in summary.iterrows():
        print("Features %d-%d : %d news items" % (row["lower"], row['upper'], row['count']))

    print("\nTotal news items - %d" % sum(summary["count"]))


"""
# Category features are classified
# similar category words are categorized
# related categories are merged to the main category
"""


def classify_category_features(feature_names, categories, related_categories):
    category_dict = {}

    # build the base feature list and related feature for each category
    for cat in categories:
        category_dict[cat] = list(filter(lambda v: re.match(cat, v), feature_names))

    category_dict["unclassified"] = []

    for cat in related_categories:
        for rc in related_categories[cat]:
            category_dict[cat] = category_dict[cat] + category_dict[rc]
            category_dict.pop(rc, None)

        category_dict[cat] = list(set(category_dict[cat]))

    return category_dict


"""
# Categorize normalized words
# produces a categorization on train data
"""


def data_naivebayes_classify_categories(category_features: dict, test_data: pd.DataFrame):
    train_feature_list = []
    test_data["normalized"] = test_data["normalized"].values.astype('U')

    for cat in category_features:
        features_list = category_features[cat]
        features_dict = {f: f for f in features_list}
        train_feature_list = train_feature_list + [(features_dict, cat)]

    classifier = naivebayes.NaiveBayesClassifier.train(train_feature_list)

    def find_match_feature(feature_text: list):
        best_score_features = {}
        best_score = 0
        for features, category in train_feature_list:
            matched = set(feature_text).intersection(set(features.values()))
            score = ((len(matched) / len(features)) if len(matched) > 0 else 0) * 100
            if best_score < score:
                best_score_features = features
                best_score = score

        return best_score_features

    labels = []
    for i, row in test_data.iterrows():
        words = word_tokenize(row["normalized"])
        #match_features = find_match_feature(words)
        #label = classifier.classify(match_features)
        label = classifier.classify({w: w for w in words})
        labels.append(label)

    return labels


"""
# Generate statistics on the model
"""


def get_prediction_metrics_accuracy(true_labels, predicted_labels):
    print('Accuracy:', np.round(metrics.accuracy_score(true_labels, predicted_labels), 2))
    print('Precision:', np.round(metrics.precision_score(true_labels, predicted_labels,
                                                         average='weighted', zero_division=True), 2))
    print('Recall:', np.round(metrics.recall_score(true_labels, predicted_labels,
                                                   average='weighted', zero_division=True), 2))
    print('F1 Score:', np.round(metrics.f1_score(true_labels, predicted_labels,
                                                 average='weighted', zero_division=True), 2))


"""
# Train the model with train data and generate predictions
# produces a categorization on test data
"""


def train_predict_classification(classifier,  train_features, train_labels, test_features):
    # build model
    classifier.fit(train_features, train_labels)
    # predict using model
    return classifier.predict(test_features)