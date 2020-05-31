gold_pos = {
    'S': 'Nn',
    'V': 'Vb',
    # 'INFN': 'If',  # V + inf
    # 'PRTF': 'Pt',  # V + partcp + plen
    # 'PRTS': 'Vp',  # V + partcp + brev
    # 'GRND': 'Dp',  # V + ger
    'A': 'Aj',
    'A-PRO': 'Aj',
    'A-NUM': 'Aj',
    # 'ADJS': 'Ap',  # A + brev
    'ADV': 'Ad',
    'ADV-PRO': 'Ad',
    'S-PRO': 'Pn',
    'PRAEDIC-PRO': 'Pd',
    'NUM': 'Nu',
    'CONJ': 'Cj',
    'PR': 'Pp',
    'PART': 'Pc',
    'PRAEDIC': 'Pd',
    'PARENTH': 'Ad',
    'A/ADV': 'Cm',
    'INTJ': 'Ij',

    'INIT': 'Zr',
    'NONLEX': 'Zr',
}

gold_animacy = {
    'anim': '_',
    'inan': '_',
    '|animation': '_',
}

gold_case = {
    'nom': 'Nm',
    'gen': 'Gn',
    'dat': 'Dt',
    'acc': 'Ac',
    'ins': 'Ab',
    'loc': 'Lc',
    'voc': 'Nm',
    'gen2': 'Gn',
    'loc2': 'Lc',
    'acc2': 'Ac',
    '|case': 'Zz',
}

gold_number = {
    'sg': '_',
    'pl': '_',
    '|number': '_',
}

gold_gender = {
    'm': '_',
    'f': '_',
    'n': '_',
    '|gender': '_',
}

gold_person = {
    '1p': '_',
    '2p': '_',
    '3p': '_',
    '|person': '_',
}

gold_aspect = {
    'pf': 'Pf',
    'ipf': 'Im',
    '|aspect': 'Zz',
}

pymorphy_all = {
    'NOUN': 'Nn',
    'VERB': 'Vb',
    'INFN': 'If',
    'PRTF': 'Pt',
    'PRTS': 'Pd', # переписать в Pd (it was Vp)
    'GRND': 'Dp',
    'ADJF': 'Aj',
    'ADJS': 'Ap',
    'ADVB': 'Ad',
    'NPRO': 'Pn',
    'NUMR': 'Nu',
    'CONJ': 'Cj',
    'PREP': 'Pp',
    'PRCL': 'Pc',
    'PRED': 'Pd',
    'COMP': 'Cm',
    'INTJ': 'Ij',

    'anim': '_',
    'inan': '_',

    'nomn': 'Nm',
    'gent': 'Gn',
    'datv': 'Dt',
    'accs': 'Ac',
    'ablt': 'Ab',
    'loct': 'Lc',
    'voct': 'Nm',
    'gen2': 'Gn',
    'loc2': 'Lc',
    'acc2': 'Ac',

    'sing': '_',
    'plur': '_',

    'masc': '_',
    'femn': '_',
    'neut': '_',

    '1per': '_',
    '2per': '_',
    '3per': '_',

    'perf': 'Pf',
    'impf': 'Im',

    'PNCT': 'PM',
    'NUMB': 'Zz', # it was NM
    'LATN': 'Zr',
    'ROMN': 'Zr',
    'UNKN': 'Zr',
}
