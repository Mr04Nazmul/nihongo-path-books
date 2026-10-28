"""Retire previous N3 import routes while awaiting the replacement PDF."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
html='<!doctype html><html lang="bn"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>N3 · Nihongo Path Books</title><main><a href="n3.html">← N3 বই</a><h1>নতুন PDF-এর অপেক্ষায়</h1><p>পুরোনো শব্দতালিকা সরানো হয়েছে। নতুন PDF থেকে পাঠ যোগ করা হবে।</p></main></html>'
for name in ['n3-bangla-words.html','n3-bangla-book.html']:(ROOT/'dist'/name).write_text(html)
