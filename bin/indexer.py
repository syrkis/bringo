# indexer.py
#   binary sentiment classification
# by: Group B

# imports
import os
import torch
from torch import nn
from tqdm import tqdm
import json 
import numpy as np
import nltk; # nltk.download('punkt')
from nltk.tokenize import word_tokenize
import gensim

# global varaibles 
sequence_length = 128
model = gensim.models.KeyedVectors.load_word2vec_format('../data/twitter.bin', binary=True)

# parsing
def parser():
    data_path = "../data/samples"
    files = os.listdir(data_path)
    domains = {}
    for file in files:
        with open(f"{data_path}/{file}", 'r') as f: 
            domain = json.loads(f.read())
            domains[file] = []
            for review in domain: 
                rating = review['overall'] >= 4
                text = word_tokenize(review.get('reviewText', ""))
                title = word_tokenize(review.get('summary', ""))
                sample = {'sentiment': rating, 'text': text, 'title': title}
                domains[file].append(sample)
        break
    return domains


# embedding this baby
def truncating(domain): 
    for idx, sample in enumerate(domain):
        sample_index = []
        for word in sample['text'][-min(sequence_length, len(sample['text'])):]:
            word_index = model.key_to_index.get(word, 1)
            sample_index.append(word_index)  
        if len(sample_index) < sequence_length: 
            sample_index = [0 for _ in range(sequence_length - len(sample_index))] + sample_index
        domain[idx]['text'] = sample_index
        title_index = []
        for word in sample['title'][-min(sequence_length, len(sample['title'])):]:
            word_index = model.key_to_index.get(word, 1)
            title_index.append(word_index) 
        if len(title_index) < sequence_length:
            title_index = [0 for _ in range(sequence_length - len(title_index))] + title_index
        domain[idx]['title'] = title_index
    return domain

# call stack
def main():
    domains = parser()
    for k, v in tqdm(domains.items()):
        domains[k] = truncating(v)
    for k, v in domains.items():
        X, y = [sample['text'] for sample in v], [float(sample['sentiment']) for sample in v]
        X, y = map(torch.tensor, [X, y]) 
        D = torch.cat((X, y.reshape(len(v), 1)), dim=1)
        with open(f'../data/npys/{k}.npy', 'wb') as f:
            np.save(f, D)  

if __name__ == "__main__":
    main()
