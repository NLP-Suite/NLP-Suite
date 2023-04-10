import os
import matplotlib.pyplot as plt


def pie_charts(docs, paths):
    
    for doc in docs:
        i_path = paths[doc]
        with open(f'{i_path}/senses', 'r') as f:
            tokens = list(set(f.read().split('\n')[:-1]))
        tokens = [tok.split('\t') for tok in tokens]
        vocab = list(set([tok[1] for tok in tokens]))
        for w in vocab: 
            o_path = f'{i_path}/clusters/{w}'
            if not os.path.exists(o_path):
                os.makedirs(o_path)
            senses = list(set([tok[-1] for tok in tokens])) 
            occs = [tok for tok in tokens if tok[1] == w]
            total = len(occs)
            values = []
            for s in senses:
                values.append(len([tok for tok in occs if tok[-1] == s]) / total)
            fig, ax = plt.subplots()
            ax.pie(values, labels=senses, autopct='%1.1f%%')
            ax.set_title(w)
            fig.savefig(f'{o_path}/{w}.png')





