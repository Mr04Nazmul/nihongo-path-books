"""Small experimental Modal translation pilot. Outputs unreviewed drafts only.

Run from repository root: modal run scripts/modal_inference.py --limit 2
Requires an authenticated Modal CLI. Output remains local, never updates ledger.
"""
import json
import pathlib
import sys
import time
import modal


MODEL = 'google/madlad400-3b-mt'
REVISION = 'main'
app = modal.App('nihongo-bengali-draft-pilot')
image = (modal.Image.debian_slim(python_version='3.11')
         .pip_install('torch==2.5.1', 'transformers==4.49.0', 'accelerate==1.3.0'))

@app.cls(image=image, gpu=['L4', 'A10', 'L40S'], timeout=600, scaledown_window=10, max_containers=1)
class Translator:
    @modal.enter()
    def load(self):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL, revision=REVISION, torch_dtype=torch.float16, device_map='auto')
        self.model.eval()

    @modal.method()
    def translate(self, item):
        import torch
        source = item['source'].get('ja')
        if not source:
            raise ValueError('This pilot accepts Japanese example sentences only')
        inputs = self.tokenizer('<2bn> ' + source, return_tensors='pt').to(self.model.device)
        with torch.inference_mode():
            output = self.model.generate(**inputs, max_new_tokens=256, do_sample=False)
        return self.tokenizer.decode(output[0], skip_special_tokens=True).strip()

@app.local_entrypoint()
def main(limit: int = 2, offset: int = 0, output: str = 'translations/modal-pilot-drafts.jsonl'):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from modal_translation_drafts import pending_items, validate_draft
    if not 1 <= limit <= 10:
        raise ValueError('Pilot limit must be 1–10 fields per run')
    if offset < 0:
        raise ValueError('offset must be nonnegative')
    path = pathlib.Path(output)
    existing = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            existing[(row['key'], row['source_sha256'], row['previous_translation_sha256'])] = row
    # Fetch more candidates so already completed records do not prevent progress.
    candidates = pending_items(1000, offset)
    selected = [i for i in candidates if i['field'].startswith('examples.') and i['source'].get('ja') and (i['key'], i['source_sha256'], i['previous_translation_sha256']) not in existing][:limit]
    if not selected:
        print('No pending pilot candidates found in selected window.')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    worker = Translator()
    for item in selected:
        error = None
        for attempt in range(2):
            try:
                response = worker.translate.remote(item)
                row = validate_draft(item, response)
                if any('\u0400' <= ch <= '\u052f' for ch in response):
                    row['flags'].append('unexpected_cyrillic_script')
                row.update(model=MODEL, revision=REVISION, created_unix=int(time.time()))
                with path.open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(row, ensure_ascii=False) + '\n')
                    stream.flush()
                print(json.dumps({'key': row['key'], 'status': row['status'], 'flags': row['flags']}, ensure_ascii=False))
                error = None
                break
            except Exception as exc:
                error = exc
                if attempt == 0:
                    time.sleep(2)
        if error is not None:
            raise RuntimeError('Draft failed; completed records remain in checkpoint') from error
