"""Bounded Japanese-to-Bengali model comparison; no corpus or ledger writes."""
import json
import modal

MODEL = "facebook/m2m100_1.2B"
SENTENCES = [
    "口にものをほおばってしゃべるな。",
    "靴のほこりをはけではらいなさい。",
    "この靴下はちぐはぐだ。",
    "車のわきの男の子をごらんなさい。",
    "こんにちは、ロジャー。とっても元気よ。",
    "大会９日目、ベスト８が出揃った。",
    "この木にしっかりつかまりなさい。",
    "今晩はパーティーがあるのかなあ。",
]
app = modal.App("nihongo-m2m-benchmark")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch==2.5.1", "transformers==4.49.0", "accelerate==1.3.0", "sentencepiece==0.2.0"
)

@app.cls(image=image, gpu=["L4", "A10", "L40S"], timeout=600, scaledown_window=10, max_containers=1)
class Translator:
    @modal.enter()
    def load(self):
        import torch
        from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
        self.tokenizer = M2M100Tokenizer.from_pretrained(MODEL)
        self.tokenizer.src_lang = "ja"
        self.model = M2M100ForConditionalGeneration.from_pretrained(
            MODEL, torch_dtype=torch.float16, device_map="auto"
        ).eval()

    @modal.method()
    def translate(self, sentences):
        import torch
        rows = []
        for source in sentences:
            inputs = self.tokenizer(source, return_tensors="pt").to(self.model.device)
            with torch.inference_mode():
                tokens = self.model.generate(
                    **inputs, forced_bos_token_id=self.tokenizer.get_lang_id("bn"),
                    max_new_tokens=128, num_beams=4,
                )
            rows.append({"source": source, "draft": self.tokenizer.decode(tokens[0], skip_special_tokens=True),
                         "model": MODEL, "status": "unreviewed"})
        return rows

@app.local_entrypoint()
def main():
    rows = Translator().translate.remote(SENTENCES)
    with open("m2m-benchmark.jsonl", "w", encoding="utf-8") as output:
        for row in rows:
            print(json.dumps(row, ensure_ascii=False))
            output.write(json.dumps(row, ensure_ascii=False) + "\n")
