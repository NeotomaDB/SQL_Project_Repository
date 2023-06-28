from collections import defaultdict

def vocabDict(data):
    """
    Obtain the units dictionary
    """
    # Todo raise statement if the dictionary does not have a 'metadata' key\
    vocab_dict = {d['column']: d['vocab'] for d in data if d['vocab'] is not None}

    # Maybe we can remove this part
    unit_cols = defaultdict(list)
    for d in data:
        if 'class' in d.keys():
            unit_cols[d['class']].append(d['column'])
    unit_cols = dict(unit_cols)

    return vocab_dict