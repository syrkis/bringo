# indexer.py
#   binary sentiment classification
# by: Group B

# imports
import os
from multiprocessing import Pool
import torch
from torch import nn
from tqdm import tqdm
import json 
import numpy as np
import nltk; # nltk.download('punkt')
from nltk.tokenize import word_tokenize
import gensim
from reader import parse

# global varaibles 
sequence_length = 128
data_path = "/home/common/datasets/amazon_review_data_2018/reviews"
# data_path = "../data/samples"
model = gensim.models.KeyedVectors.load_word2vec_format('../data/twitter.bin', binary=True)

# parsing
def parser(file_name):
	all_reviews = []
	for review in parse(f"{data_path}/{file_name}"): 
		rating = review['overall'] >= 4
		text = word_tokenize(review.get('reviewText', ""))
		text = truncating(text)
		title = word_tokenize(review.get('summary', ""))
		title = truncating(title)
		D = text + title + [rating]
		all_reviews.append(D)
	data = torch.tensor(all_reviews)
    file = filename.split('.')[0]
	with open(f"data/npys/{file}", "wb") as f:
		np.save(f,data)
	print(file_name,"DONE")

# embedding this baby
def truncating(sample): 
	sample_index = [model.key_to_index.get(s, 1) for s in sample[-min(sequence_length, len(sample)):]]
	sample_index = [0 for _ in range(sequence_length-len(sample_index))] + sample_index
	return sample_index

# call stack
def main():
    targets = [s for s in os.listdir(data_path) if s.split('.')[0] not in os.listdir("data/npys")]
    with Pool() as p:
		p.map(parser, targets)

if __name__ == "__main__":
	main()
