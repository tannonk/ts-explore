#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __Author__: "Tannon Kew"
# __Date__: 2023-05-31
# __email__: kew@cl.uzh.ch

"""

Example usage:
    python annotate_operations.py -i ../llm_simplification_results/ground_truth/asset.test.jsonl -s source -t model_output

"""

from typing import List, Tuple, Dict, Union
import argparse
from tqdm import tqdm
import json
from pathlib import Path
from mosestokenizer import MosesTokenizer

from py4j.java_gateway import JavaGateway

def parse_args():

    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir_or_file", type=str, default=None, help="path to directory containing multiple jsonl files or a single jsonl file to be annotated")
    ap.add_argument("-s", "--source_key", type=str, default="source", help="key in jsonl file for source sentence")
    ap.add_argument("-t", "--target_key", type=str, default="model_output", help="key in jsonl file for target sentence")
    ap.add_argument("-v", "--verbose", action="store_true", help="print verbose output")
    return ap.parse_args()

def get_outfile(input_file: str) -> str:
    outfile = str(Path(input_file).with_suffix('.editops'))
    return outfile

def result_to_dict(input_string: str) -> List[Dict[str, Union[str, None]]]:
    """
    input_string = "DELETE,is,null\tDELETE,composed,null"
    output_dict = {["operation": "DELETE", "source": "is", "target": null], ["operation": "DELETE", "source": "composed", "target": null]}
    """
    if input_string == '':
        return [{'operation': None, 'source': None, 'target': None}]
    else:
        return [{'operation': op, 'source': src, 'target': None if tgt.lower() == 'null' else tgt}
                for op, src, tgt in (substr.split('|||') for substr in input_string.split("\t"))]

def annotate_file(input_file, source_key='source', target_key='model_output', verbose=False):

    gateway = JavaGateway()
    edit_distance = gateway.entry_point.getEditDistance()
    
    tokenize = MosesTokenizer('en')
    
    outfile = get_outfile(input_file)
    
    with open(input_file, 'r', encoding='utf8') as inf:
        with open(outfile, 'w', encoding='utf8') as outf:
            for line in tqdm(inf, desc=f"Annotating edit operations in {input_file}" if verbose else None, disable=not verbose):
                data = json.loads(line.strip())
                source, target = ' '.join(tokenize(data[source_key])), ' '.join(tokenize(data[target_key]))
                result = edit_distance.calculate_all(source, target)
                result = result_to_dict(result)
                # data["edit_ops"] = result
                outf.write(json.dumps(result, ensure_ascii=False) + "\n")

    tokenize.close()
    if verbose:
        print(f"Edit operations written to {outfile}")
    
if __name__ == "__main__":
    args = parse_args()
    
    if Path(args.input_dir_or_file).is_dir():
        c = 0
        for infile in Path(args.input_dir_or_file).glob('*.jsonl'):
            annotate_file(infile, args.source_key, args.target_key, args.verbose)
            c += 1
        if c == 0:
            raise ValueError(f"No jsonl files found in {args.input_dir_or_file}")
        else:
            print(f"Processed {c} files in {args.input_dir_or_file}")
    else:
        annotate_file(args.input_dir_or_file, args.source_key, args.target_key, args.verbose)
