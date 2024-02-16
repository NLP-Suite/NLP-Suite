import os
import matplotlib.pyplot as plt


def sense_bar_chart(Word2Vec_Dir,  figsize=(20, 10), fontsize=32):
     
    with open(f'{Word2Vec_Dir}/output/senses', 'r') as f:
        tokens = list(set(f.read().split('\n')[:-1]))
    tokens = [tok.split('\t') for tok in tokens]
    vocab = list(set([tok[1] for tok in tokens]))
    v_paths = []
    for w in vocab: 
        chart_title = f"Frequency Distribution of Senses of '{w}'"
        senses = sorted(list(set([tok[-1] for tok in tokens]))) 
        sense_labels = [f'Sense {sense}' for sense in senses]
        occs = [tok for tok in tokens if tok[1] == w]
        total = len(occs)
        values = []
        for s in senses:
            values.append(len([tok for tok in occs if tok[-1] == s]) / total)
        fig, ax = plt.subplots(figsize=figsize)
        ax.bar(senses, values)
        ax.set_title(chart_title, fontsize=fontsize)
        ax.tick_params(axis='both', labelsize=fontsize)
        ax.set_xticklabels(sense_labels)
        plt.ylabel('Relative Frequency', fontsize=fontsize)
        fig.savefig(f'{Word2Vec_Dir}/results/{w}/{chart_title}.png')
        v_paths.append(f'{Word2Vec_Dir}/results/{w}/{chart_title}.png')
    
    return v_paths




