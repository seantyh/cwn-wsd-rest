import CWN_WSD

def wsd_warmup():
    CWN_WSD.warmup()

def wsd(tagged_list):
    senses_list = CWN_WSD.wsd(tagged_list)
    return senses_list