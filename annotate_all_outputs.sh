#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# outputs_dir="/home/user/kew/projects/llm_simplification_results"
outputs_dir="/srv/scratch1/kew/llm_ats/outputs"

model_dirs=(
    # bloom
    # bloom-1b1
    # bloom-3b
    # bloom-560m
    # bloom-7b1
    # bloomz
    # bloomz-1b1
    # bloomz-3b
    # bloomz-560m
    # bloomz-7b1
    # cohere-command-light
    # flan-t5-base
    # flan-t5-large
    # flan-t5-small
    # flan-t5-xl
    # flan-t5-xxl
    # flan-ul2
    # gpt-j-6b
    # gpt-neox-20b
    ground_truth
    # llama-13b
    # llama-30b
    # llama-65b
    # llama-7b
    muss
    # openai-gpt-3.5-turbo
    # openai-text-ada-001
    # openai-text-babbage-001
    # openai-text-curie-001
    # openai-text-davinci-002
    # openai-text-davinci-003
    # opt-13b
    # opt-1.3b
    # opt-30b
    # opt-66b
    # opt-6.7b
    # opt-iml-max-1.3b
    # opt-iml-max-30b
    # t0
    # t0-3b
    # t0pp
    # t5-base-lm-adapt
    # t5-large-lm-adapt
    # t5-small-lm-adapt
    # t5-xl-lm-adapt
    # t5-xxl-lm-adapt
    # ul2
)

for model_dir in "${model_dirs[@]}"; do
    python annotate_operations.py "$outputs_dir/$model_dir" --source_key "source" --target_key "model_output"
done
