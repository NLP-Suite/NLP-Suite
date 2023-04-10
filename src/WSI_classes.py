import os
tcache_path = f'{os.getcwd()}/cache'
if not os.path.exists(tcache_path):
    os.makedirs(tcache_path)
os.environ['TRANSFORMERS_CACHE'] = tcache_path
import sklearn
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict, Counter
import random
from tqdm import tqdm
import torch
from torch import nn
import pickle
import numpy as np
from transformers import BertTokenizer, BertModel


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

SEED = 0
batch_size = 32
dropout_rate = 0.25
bert_dim = 768


class Clusterer():

    def __init__(self, tokenizer, model_name):

        self.tokenizer = tokenizer
        self.model = model_name
        self.model.eval()
        self.model.to(device)


    def get_batches(self, sentences, max_batch):
    
        # each item in these lists is a sentence
        all_data = [] # indexed tokens, or word IDs
        all_words = [] # tokenized_text, or original words
        all_masks = []
        all_users = []
        for sentence in sentences:
            marked_text = sentence[1]
            tokenized_text_all = self.tokenizer.tokenize(marked_text)
            for i in range(0, len(tokenized_text_all), 510):
                tokenized_text = tokenized_text_all[i:i+510]
                indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
                indexed_tokens = self.tokenizer.build_inputs_with_special_tokens(indexed_tokens)
                all_data.append(indexed_tokens)
                all_words.append(tokenized_text)
                all_masks.append(list(np.ones(len(indexed_tokens))))
                all_users.append(sentence[0])
    
        lengths = np.array([len(l) for l in all_data])
        ordering = np.argsort(lengths)
        # each item in these lists is a sentence
        ordered_data = [None for i in range(len(all_data))]
        ordered_words = [None for i in range(len(all_data))]
        ordered_masks = [None for i in range(len(all_data))]
        ordered_users = [None for i in range(len(all_data))]
        for i, ind in enumerate(ordering):
            ordered_data[i] = all_data[ind]
            ordered_words[i] = all_words[ind]
            ordered_masks[i] = all_masks[ind]
            ordered_users[i] = all_users[ind]
        # each item in these lists is a batch of sentences
        batched_data = []
        batched_words = []
        batched_masks = []
        batched_users = []
        i = 0
        current_batch = max_batch
        while i < len(ordered_data):
            batch_data = ordered_data[i:i+current_batch]
            batch_words = ordered_words[i:i+current_batch]
            batch_mask = ordered_masks[i:i+current_batch]
            batch_users = ordered_users[i:i+current_batch]
    
            max_len = max([len(sent) for sent in batch_data])
            for j in range(len(batch_data)):
                blen = len(batch_data[j])
                for k in range(blen, max_len):
                    batch_data[j].append(0)
                    batch_mask[j].append(0)
            batched_data.append(torch.LongTensor(batch_data))
            batched_words.append(batch_words)
            batched_masks.append(torch.FloatTensor(batch_mask))
            batched_users.append(batch_users)
            i += current_batch
            if max_len > 100:
                current_batch = 12
            if max_len > 200:
                current_batch = 6
        return batched_data, batched_words, batched_masks, batched_users
    
    
    def get_embeddings(self, batched_data, batched_words, batched_masks, batched_users, word):
    
        word = word.lower()
        ret = []
        do_wordpiece = True
        for b in range(len(batched_data)):
            # each item in these lists/tensors is a sentence
            tokens_tensor = batched_data[b].to(device)
            atten_tensor = batched_masks[b].to(device)
            words = batched_words[b]
            users = batched_users[b]
            with torch.no_grad():
    #                _, _, encoded_layers = self.model(tokens_tensor, attention_mask=atten_tensor, token_type_ids=None)
                o = self.model(tokens_tensor, attention_mask=atten_tensor, token_type_ids=None)
                encoded_layers = o['hidden_states']
            for sent_i in range(len(words)):
                for token_i in range(len(words[sent_i])):
                    if batched_masks[b][sent_i][token_i] == 0: continue
                    w = words[sent_i][token_i]
                    next_w = ''
                    if (token_i + 1) < len(words[sent_i]):
                        next_w = words[sent_i][token_i+1]
                    if w != word and '##' not in w and '##' not in next_w: continue
                    if w == word:
                        do_wordpiece = False
                    hidden_layers = []
                    for layer_i in range(1, 5):
                        vec = encoded_layers[-layer_i][sent_i][token_i]
                        hidden_layers.append(vec)
                    # concatenate last four layers
                    rep = torch.cat((hidden_layers[0], hidden_layers[1],
                                hidden_layers[2], hidden_layers[3]), 0)
                    ret.append((w, rep.cpu().numpy().reshape(1, -1)[0]))
    
        return (ret, do_wordpiece)
    
    
    def group_wordpiece(self, embeddings, word, do_wordpiece):
        '''
        - puts together wordpiece vectors
        - only piece them together if embeddings does not
        contain the vocab word of interest
        - filters vectors so we only have vectors for the word of interest
        '''
        word = word.lower()
        data = []
        prev_w = (None, None)
        ongoing_word = []
        ongoing_rep = []
        for i, tup in enumerate(embeddings):
            if not do_wordpiece:
                if tup[0] == word:
                    data.append(tup[1])
            else:
                if tup[0].startswith('##'):
                    if not prev_w[0].startswith('##'):
                        ongoing_word.append(prev_w[0])
                        ongoing_rep.append(prev_w[1])
                    ongoing_word.append(tup[0][2:])
                    ongoing_rep.append(tup[1])
                else:
                    if ''.join(ongoing_word) == word:
                        data.append(np.mean(ongoing_rep, axis=0).flatten())
                    ongoing_word = []
                    ongoing_rep = []
            prev_w = tup
        if ''.join(ongoing_word) == word:
            data.append(np.mean(ongoing_rep, axis=0).flatten())
        np.random.shuffle(data)
    
    #        return np.array(data)[:500]
        return np.array(data)
    
    
    def cluster_embeddings(self, data, k_range, ID=None, dim_reduct=None, rs=SEED, lamb=10000, finetuned=False, a_s=None):
    
            if a_s is None:
                ks = range(k_range[0], k_range[1])
            else:
                ks = range(a_s[0], a_s[1])
            centroids = {}
            rss = np.zeros(len(ks))
            for i, k in enumerate(ks):
                km = KMeans(k, random_state=rs)
                km.fit(data)
                rss[i] = km.inertia_
                centroids[k] = km.cluster_centers_
            crits = []
            for i in range(len(ks)):
                k = ks[i]
                crit = rss[i] + lamb*k
                crits.append(crit)
            best_k = np.argmin(crits)
    
            return centroids[ks[best_k]]
    
####

class Matcher():

    def __init__(self, tokenizer, model_name):

        self.tokenizer = tokenizer
        self.model = model_name
        self.model.eval()
        self.model.to(device)


    def get_batches(self, sentences, max_batch, test=False):
    
        # each item in these lists is a sentence
        all_data = [] # indexed tokens, or word IDs
        all_words = [] # tokenized_text, or original words
        all_masks = []
        all_users = []
        for sentence in sentences:
            marked_text = sentence[1]
            tokenized_text_all = self.tokenizer.tokenize(marked_text)
            for i in range(0, len(tokenized_text_all), 510):
                tokenized_text = tokenized_text_all[i:i+510]
                indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
                indexed_tokens = self.tokenizer.build_inputs_with_special_tokens(indexed_tokens)
                all_data.append(indexed_tokens)
                all_words.append(tokenized_text)
                all_masks.append(list(np.ones(len(indexed_tokens))))
                all_users.append(sentence[0])
    
        lengths = np.array([len(l) for l in all_data])
        ordering = np.argsort(lengths)
        # each item in these lists is a sentence
        ordered_data = [None for i in range(len(all_data))]
        ordered_words = [None for i in range(len(all_data))]
        ordered_masks = [None for i in range(len(all_data))]
        ordered_users = [None for i in range(len(all_data))]
        for i, ind in enumerate(ordering):
            ordered_data[i] = all_data[ind]
            ordered_words[i] = all_words[ind]
            ordered_masks[i] = all_masks[ind]
            ordered_users[i] = all_users[ind]
        # each item in these lists is a batch of sentences
        batched_data = []
        batched_words = []
        batched_masks = []
        batched_users = []
        i = 0
        current_batch = max_batch
        while i < len(ordered_data):
            batch_data = ordered_data[i:i+current_batch]
            batch_words = ordered_words[i:i+current_batch]
            batch_mask = ordered_masks[i:i+current_batch]
            batch_users = ordered_users[i:i+current_batch]
    
            max_len = max([len(sent) for sent in batch_data])
            for j in range(len(batch_data)):
                blen = len(batch_data[j])
                for k in range(blen, max_len):
                    batch_data[j].append(0)
                    batch_mask[j].append(0)
            batched_data.append(torch.LongTensor(batch_data))
            batched_words.append(batch_words)
            batched_masks.append(torch.FloatTensor(batch_mask))
            batched_users.append(batch_users)
            i += current_batch
            if max_len > 100:
                current_batch = 12
            if max_len > 200:
                current_batch = 6
    
        return batched_data, batched_words, batched_masks, batched_users
    
    
    def load_centroids(self, vocab, path, added_centroids=None, rs=SEED):
    
        if added_centroids is None:
            centroids_folder = f'{path}/centroids'
        else:
            centroids_folder = f'{path}/added_centroids_{added_centroids[0]}_{added_centroids[1]}'
        centroids_d = {}
        for w in tqdm(sorted(vocab)):
            if f'{w}.npy' not in os.listdir(centroids_folder): continue
            centroids = np.load(f'{centroids_folder}/{w}.npy', allow_pickle=True)
            centroids_d[w] = centroids
    
        return centroids_d
    
    
    def batch_match(self, outfile, centroids_d, data_dict):
    
        for tok in data_dict:
            rep_list = data_dict[tok]
            IDs = []
            reps = []
            for tup in rep_list:
                IDs.append(tup[0])
                reps.append(tup[1])
            reps = np.array(reps)
            centroids = centroids_d[tok]
            assert reps.shape[1] == centroids.shape[1]
            sims = cosine_similarity(reps, centroids) # IDs x n_centroids
            labels = np.argmax(sims, axis=1)
            for i, _ in enumerate(IDs):
                outfile.write(str(IDs[i]) + '\t' + tok + '\t' + str(labels[i]) + '\n')
    
    
    def get_embeddings_and_match(self, batched_data, batched_words, batched_masks, batched_users, centroids_d, o_path, added_centroids=None):
    
        if added_centroids is None:
            outfile = open(f'{o_path}/senses', 'w')
        else:
            outfile = open(f'{o_path}/added_senses_{added_centroids[0]}_{added_centroids[1]}', 'w')
        vocab = set(centroids_d.keys())
        ret = []
        # variables for grouping wordpiece vectors
        prev_w = (None, None, None)
        ongoing_word = []
        ongoing_rep = []
        data_dict = defaultdict(list) # { word : [(user, rep)] }
        for b, _ in tqdm(enumerate(batched_data), total=len(batched_data), desc='Matching...'):
            # each item in these lists/tensors is a sentence
            tokens_tensor = batched_data[b].to(device)
            atten_tensor = batched_masks[b].to(device)
            words = batched_words[b]
            users = batched_users[b]
            with torch.no_grad():
    #                _, _, encoded_layers = self.model(tokens_tensor, attention_mask=atten_tensor, token_type_ids=None)
                o = self.model(tokens_tensor, attention_mask=atten_tensor, token_type_ids=None)
                encoded_layers = o['hidden_states']
            for sent_i in range(len(words)):
                for token_i in range(len(words[sent_i])):
                    if batched_masks[b][sent_i][token_i] == 0: continue
                    w = words[sent_i][token_i]
                    next_w = ''
                    if (token_i + 1) < len(words[sent_i]):
                        next_w = words[sent_i][token_i+1]
                    if w not in vocab and '##' not in w and '##' not in next_w: continue
                    # get vector
                    hidden_layers = []
                    for layer_i in range(1, 5):
                        vec = encoded_layers[-layer_i][sent_i][token_i]
                        hidden_layers.append(vec)
                    # concatenate last four layers
                    vector = torch.cat((hidden_layers[0], hidden_layers[1],
                                hidden_layers[2], hidden_layers[3]), 0)
                    vector =  vector.cpu().numpy().reshape(1, -1)[0]
                    # piece together wordpiece vectors if necessary
                    if not w.startswith('##'):
                        if len(ongoing_word) == 0 and prev_w[0] is not None:
                            data_dict[prev_w[0]].append((prev_w[1], prev_w[2]))
                        elif prev_w[0] is not None:
                            rep = np.array(ongoing_rep)
                            rep = np.mean(rep, axis=0).flatten()
                            tok = ''
                            for t in ongoing_word:
                                if t.startswith('##'): t = t[2:]
                                tok += t
                            if tok in vocab:
                                data_dict[tok].append((prev_w[1], rep))
                        ongoing_word = []
                        ongoing_rep = []
                    else:
                        if len(ongoing_word) == 0 and prev_w[0] is not None:
                            ongoing_word.append(prev_w[0])
                            ongoing_rep.append(prev_w[2])
                        ongoing_word.append(w)
                        ongoing_rep.append(vector)
                    prev_w = (w, users[sent_i], vector)
            if b % 10 == 0:
                # do centroid matching in batches
                self.batch_match(outfile, centroids_d, data_dict)
                data_dict = defaultdict(list)
        # fencepost
        if len(ongoing_word) == 0 and prev_w[0] is not None:
            data_dict[prev_w[0]].append((prev_w[1], prev_w[2]))
        elif prev_w[0] is not None:
            rep = np.array(ongoing_rep)
            rep = np.mean(rep, axis=0).flatten()
            tok = ''
            for t in ongoing_word:
                if t.startswith('##'): t = t[2:]
                tok += t
            if tok in vocab:
                data_dict[tok].append((prev_w[1], rep))
        self.batch_match(outfile, centroids_d, data_dict)
        outfile.close()
    
