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
        cedict_path = Path(__file__).parent / "cedict/cedict.txt"
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
    
def syn2str(synsets):
    return [syn.name() for syn in synsets]

def get_sense_clouds(sid: str):
    cwn = get_cwn_inst()
    sense = CwnSense(sid, cwn)
    rels = [(x[0], x[1].id, x[1].head_word, x[1].pos, x[1].definition) for x 
              in sense.semantic_relations 
              if x[2] == "forward"]
    
    pwn = []    
    if sense.pwn_synsets:        
        pwn_map = sense.pwn_synsets[0][1]
        if pwn_map.has_wn30:
            pwn = ["generic", pwn_map.wn30_synset]
        else:
            pwn = []
        
    else:
        cemap = get_cemap()
        pos = sense.pos[0].lower() if sense.pos else ""
        pos = pos if pos in ("nv") else None
        lemma = sense.lemmas[0].lemma if sense.lemmas else ""
        if lemma in cemap:
            syn = find_synset(cemap[sense.lemmas[0].lemma], pos=pos)            
            pwn = ["generic", syn] if syn else []
    
    if pwn:
        syn = pwn[1]        
        hypers = syn.hypernym_paths()
        pwn_onto = {
            "hypernyms": syn2str(hypers[0]) if hypers else [],
            "hyponyms": syn2str(syn.hyponyms()),
            "holonyms": syn2str(syn.member_holonyms() + syn.part_holonyms() + syn.substance_holonyms()),
            "meronyms": syn2str(syn.member_meronyms() + syn.part_meronyms() + syn.substance_meronyms())
        }
    else:
        pwn_onto = {}    
    
    pwn_ret = [pwn[0], pwn[1].name()] if pwn else []

    return {
        "relations": rels,
        "pwn": pwn_ret,
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
            "examples": "\n".join(sense.all_examples())
        }
    else:
        sense = wn.synset(sid)
        sdata = {
            "lemma": sense.lemmas()[0].name(),
            "pos": sense.pos(),
            "definition": sense.definition(),
            "examples": "\n".join(sense.examples())
        }
    return sdata

def get_lemma_senses(lemma):
    cwn = get_cwn_inst()
    senses = cwn.find_all_senses(lemma)
    ret_data = [{
        "id": sense.id,
        "pos": sense.pos,
        "definition": sense.definition
    } for sense in senses]
    return ret_data