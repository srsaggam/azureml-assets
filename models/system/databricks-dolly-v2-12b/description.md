The dolly-v2-12b model is a large, instruction-following language model created by Databricks, Inc. and is licensed for commercial use. It is based on EleutherAI’s Pythia-12b and was trained on a 15,000-record instruction corpus generated by Databricks employees, which was released under a CC-BY-SA license. It is not a state-of-the-art model, but it does exhibit high-quality instruction-following behavior that is not characteristic of the foundation model on which it is based.

> The above summary was generated using ChatGPT. Review the <a href="https://huggingface.co/databricks/dolly-v2-12b" target="_blank">original model card</a> to understand the data used to train the model, evaluation metrics, license, intended uses, limitations and bias before using the model.

### Sample inputs and outputs (for real-time inference)

```json
{
    "input_data": {
        "input_string": ["Hello! How are you?" , "Explain to me the difference between nuclear fission and fusion."]
    }
}
```

#### Sample output
```json
[
  "As a Large Language Model (LLM), I don't have feelings like humans do. But I can say that I will output this response tomorrow when I'm ready.",
  "Nuclear fission and fusion are different methods of releasing energy from nuclear reactions. Nuclear fission involves splitting an atomic nucleus and releasing two or more smaller atomic nuclei and nuclear fusion is a type of nuclear reaction in which two atomic nuclei merge to form a bigger atomic nucleus and release energy."
]
```