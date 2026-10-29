import json,re,unicodedata
from pathlib import Path
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
P=args.output.resolve()
if P.is_relative_to(Path(__file__).resolve().parents[2]):raise SystemExit('Drafts belong outside the public repository')
rows=json.loads((P/'collected.json').read_text())
def normalize(s):return re.sub(r'\s+','',unicodedata.normalize('NFKC',s)).replace('：',':')
matched=0
for e in rows:
 exercise=normalize(e['exercise']);script=normalize(e['transcript'])
 parts=re.split(r'\(\)',exercise)
 pattern='(.+?)'.join(re.escape(s) for s in parts)
 match=re.fullmatch(pattern,script)
 answers=list(match.groups()) if match and len(parts)>1 else []
 e['sourceAnswers']=answers;e['answerExtraction']='exact-normalized-alignment' if answers else 'manual-review-required'
 e['ruby']=[[line] for line in e['transcript'].splitlines()]
 e['verification']['quizReviewed']=False
 if answers:
  matched+=1
  # Derived practice, never mislabeled as an original MLC multiple-choice quiz.
  e['quizOrigin']='Nihongo Path draft adaptation of MLC fill-in-the-blank exercise'
  bank=list(dict.fromkeys(answers))
  e['quiz']=[]
  for i,answer in enumerate(answers):
   wrong=[s for s in bank if s!=answer][:3]
   if not wrong:continue
   choices=wrong+[answer];answerIndex=len(choices)-1
   e['quiz'].append({'prompt':{'en':f'Which expression fills blank {i+1}?','bn':f'{i+1} নম্বর শূন্যস্থানে কোনটি হবে?'},'choices':[{'en':s,'bn':s} for s in choices],'answer':answerIndex,'explanation':{'en':'Compare this blank with the full Japanese transcript.','bn':'পূর্ণ জাপানি স্ক্রিপ্টের সঙ্গে এই শূন্যস্থান মিলিয়ে দেখুন।'}})
(P/'answer-drafts.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print('Exact answer alignment:',matched,'of',len(rows))
