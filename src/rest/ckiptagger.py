from ckiptagger import construct_dictionary, WS, POS, NER
from typing import List, Union
from pathlib import Path

model_path = Path(__file__).parent / "data"
ws = None
pos = None

def tag(sentence_list: Union[str, List[str]]):
    global ws, pos
    if ws is None:
        ws = WS(model_path)
    if pos is None:
        pos = POS(model_path)
    if isinstance(sentence_list, str):
        sentence_list = [sentence_list]

    words_list = ws(sentence_list)
    pos_list = pos(words_list)

    tagged_list = []
    for words, poses in zip(words_list, pos_list):
        tagged_list.append([(w, p) for w, p in zip(words, poses)])
    
    return tagged_list
