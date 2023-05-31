from typing import List, Tuple, Dict, Union
import argparse
from tqdm import tqdm
import json
from pathlib import Path
from mosestokenizer import MosesTokenizer

from py4j.java_gateway import JavaGateway

def parse_args():

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input_file", type=str, required=True, help="path to jsonl file containing input/output pairs to be annotated")
    ap.add_argument("-s", "--source_key", type=str, default="source", help="key in jsonl file for source sentence")
    ap.add_argument("-t", "--target_key", type=str, default="model_output", help="key in jsonl file for target sentence")
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

def main(args):

        
    gateway = JavaGateway()
    edit_distance = gateway.entry_point.getEditDistance()
    
    tokenize = MosesTokenizer('en')
    
    outfile = get_outfile(args.input_file)
    
    with open(args.input_file, 'r', encoding='utf8') as inf:
        with open(outfile, 'w', encoding='utf8') as outf:
            for line in tqdm(inf, desc=f"Annotating edit operations in {args.input_file}"):
                data = json.loads(line.strip())
                source, target = ' '.join(tokenize(data[args.source_key])), ' '.join(tokenize(data[args.target_key]))
                result = edit_distance.calculate_all(source, target)
                result = result_to_dict(result)
                data["edit_ops"] = result
                outf.write(json.dumps(data, ensure_ascii=False) + "\n")

    tokenize.close()

    print(f"Edit operations written to {outfile}")

if __name__ == "__main__":
    args = parse_args()
    main(args)