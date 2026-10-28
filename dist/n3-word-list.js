'use strict';
(() => {
 const byId=id=>document.getElementById(id), size=60, number=n=>n.toLocaleString('bn-BD');
 let entries=[],matches=[],page=0;
 if(location.pathname.endsWith('n3-bangla-book.html'))byId('category').value='all';
 const normalize=s=>String(s).normalize('NFKC').toLowerCase().replace(/[০-৯]/g,c=>'০১২৩৪৫৬৭৮৯'.indexOf(c));
 function filter(){
  const query=normalize(byId('find').value.trim()),category=byId('category').value,pdf=byId('pdfPage').value;
  matches=entries.filter(e=>(category==='all'||e.entry_type===category)&&(!pdf||e.source_page===Number(pdf))&&(!query||normalize([e.word,e.reading,e.locales.bn.meaning,e.source_serial].join(' ')).includes(query)));
  page=0;render();
 }
 function cell(row,text,className,lang){const td=document.createElement('td');if(className)td.className=className;if(lang)td.lang=lang;td.textContent=text;row.append(td);return td;}
 function render(){
  const body=byId('entries');body.replaceChildren();
  for(const e of matches.slice(page*size,(page+1)*size)){
   const tr=document.createElement('tr');cell(tr,number(e.source_serial));cell(tr,number(e.source_page));
   const td=cell(tr,''),word=document.createElement('span'),reading=document.createElement('span');
   word.className='jp';word.lang='ja';word.textContent=e.word;td.append(word);
   if(e.reading&&e.reading!==e.word){reading.className='reading';reading.lang='ja';reading.textContent=e.reading;td.append(reading);}
   cell(tr,e.locales.bn.meaning,'bn','bn');body.append(tr);
  }
  if(!matches.length){const tr=document.createElement('tr'),td=cell(tr,'কোনো এন্ট্রি পাওয়া যায়নি। অন্য শব্দ বা পৃষ্ঠা দিয়ে খুঁজুন।');td.colSpan=4;body.append(tr);}
  byId('count').textContent=`${number(matches.length)}টি এন্ট্রি পাওয়া গেছে`;
  byId('pageNumber').textContent=matches.length?`${number(page+1)} / ${number(Math.ceil(matches.length/size))}`:'০ / ০';
  byId('prev').disabled=page===0;byId('next').disabled=(page+1)*size>=matches.length;
 }
 for(const id of ['find','pdfPage'])byId(id).addEventListener('input',filter);
 byId('category').addEventListener('change',filter);
 for(const [id,delta] of [['prev',-1],['next',1]])byId(id).onclick=()=>{page+=delta;render();byId('count').scrollIntoView({block:'start'});};
 async function load(){try{byId('error').hidden=true;const r=await fetch('data/n3-word-import.json?v=word-import-1');if(!r.ok)throw Error(r.status);const data=await r.json();if(!Array.isArray(data.entries)||data.entries.length!==2363)throw Error('Incomplete import');entries=data.entries;filter();}catch{byId('error').hidden=false;byId('count').textContent='তালিকা লোড হয়নি';}}
 byId('retry').onclick=load;load();
})();
