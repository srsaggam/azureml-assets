| 	| |
| -- | -- |
| Score range |	Integer [1-5]: where 1 is bad and 5 is good |
| What is this metric? | Measures the similarity between a source data (ground truth) sentence and the generated response by an AI model. |
| How does it work? | The GPT-similarity measure evaluates the likeness between a ground truth sentence (or document) and the AI model's generated prediction. This calculation involves creating sentence-level embeddings for both the ground truth and the model's prediction, which are high-dimensional vector representations capturing the semantic meaning and context of the sentences. |
| When to use it? |	Use it when you want an objective evaluation of an AI model's performance, particularly in text generation tasks where you have access to ground truth responses. GPT-similarity enables you to assess the generated text's semantic alignment with the desired content, helping to gauge the model's quality and accuracy. |
| What does it need as input? |	Query, Ground Truth Response, Generated Response |
