import re
from typing import List
from CwnGraph import CwnBase, CwnSense
from nltk.corpus import wordnet as wn
from pathlib import Path
import cedict

__cwn = None
__cemap = None

def get_cemap():
    global __cemap
    if not __cemap:
        cedict_path = Path(__file__).parent / "../src/rest/cedict/cedict.txt"
        infile = open(cedict_path, "r", encoding="UTF-8")
        __cemap = {}
        for ch, chs, pinyin, defs, variants, mw in cedict.iter_cedict(infile):        
            __cemap.setdefault(ch, []).extend(defs)
    return __cemap


def get_cwn_inst():
    global __cwn
    if not __cwn:
        __cwn = CwnBase()
    return __cwn

def find_synset(candids: List[str], pos=None): 
    pre_pat = re.compile("^to ")
    wn_syns = []
    for candid_x in candids:
        probe = pre_pat.sub("", candid_x)
        wn_syns = wn.synsets(probe, pos=pos)
        if wn_syns:
            break    
    return wn_syns[0] if len(wn_syns) > 0 else []
    

def get_sense_clouds(sid: str):
    cwn = get_cwn_inst()
    sense = CwnSense(sid, cwn)
    rels = [x for x 
              in sense.semantic_relations 
              if x[2] == "forward"]
    pwn = sense.pwn_synsets[0]
    if not pwn:
        cemap = get_cemap()
        syn = find_synset(cemap(sense.lemmas[0].lemma))
        if syn:
            pwn = ["generic", syn]
    
    if pwn:
        syn = pwn[1]
        hypers = syn.hypernym_paths()
        pwn_onto = {
            "hypernyms": hypers[0] if hypers else [],
            "hyponyms": syn.hyponyms(),
            "holonyms": syn.member_holonyms() + syn.part_holonyms() + syn.substance_holonyms(),
            "meronyms": syn.member_meronyms() + syn.part_meronyms() + syn.substance_meronyms()
        }
    else:
        pwn_onto = {}    
    

    return {
        "relations": rels,
        "pwn": pwn,
        "pwn_onto": pwn_onto        
    }
  
def get_sense_data(sid):
    cwn = get_cwn_inst()
    if sid in cwn.V:
        sense = CwnSense(sid, cwn)
        sdata = {
            "lemma": sense.lemmas[0].lemma if sense.lemmas else "",
            "pos": sense.pos, 
            "definition": sense.definition,
            "examples": "\n".join(sense.definition)
        }
    else:
        sense = wn.synset(sid)
        sdata = {
            "lemma": sense.lemmas[0].name(),
            "pos": sense.pos(),
            "definition": sense.definition(),
            "examples": "\n".join(sense.examples())
        }
    return sdata
