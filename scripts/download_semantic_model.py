"""Obtain model files only; no resume data is sent to the repository."""
import json
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download

root=Path(__file__).resolve().parent.parent
repo='sentence-transformers/all-MiniLM-L6-v2'
revision=HfApi().model_info(repo).sha
target=root/'models/all-MiniLM-L6-v2'
snapshot_download(repo,revision=revision,local_dir=target,allow_patterns=['config.json','config_sentence_transformers.json','modules.json','sentence_bert_config.json','tokenizer.json','tokenizer_config.json','special_tokens_map.json','vocab.txt','model.safetensors','1_Pooling/config.json','README.md'])
(target/'model-reference.json').write_text(json.dumps({'repository':repo,'revision':revision,'purpose':'Local semantic matching; pretrained, not fine-tuned for recruitment'},indent=2),encoding='utf-8')
print('Local model:',target)
print('Pinned revision:',revision)
