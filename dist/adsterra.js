/* One responsive banner, shown for five seconds on book entry, then kept inline. */
(()=>{'use strict';const cfg=window.NIHONGO_ADSTERRA;if(!cfg?.enabled)return;
 const desktop=matchMedia('(min-width: 768px)').matches,u=desktop?cfg.desktop:cfg.mobile;
 if(!u||!/^\w{32}$/.test(u.key)||u.src!==`https://bauval.org/22/${u.key}`)return;
 if(!((u.width===320&&u.height===50)||(u.width===300&&u.height===250)))return;
 const bookPage=/\/(?:n[1-5]|extra)\.html$/.test(window.location.pathname);
 const bookOpen=bookPage&&cfg.bookOpen?.enabled;
 const section=document.createElement('section');section.id='adsterraPlacement';section.className='ad-panel adsterra-panel';section.setAttribute('aria-label','Advertisement');const label=document.createElement('small');section.append(label);
 const frame=document.createElement('iframe');frame.title='Advertisement';frame.src=desktop?'adsterra-banner-desktop.html':'adsterra-banner-mobile.html';frame.width=u.width;frame.height=u.height;frame.loading=bookOpen?'eager':'lazy';frame.style.cssText='display:block;margin:12px auto;border:0;max-width:100%';if(!bookOpen||cfg.bookOpen.mode!=='countdown')section.append(frame);
 document.querySelector('main')?.insertAdjacentElement(bookOpen?'beforebegin':'afterend',section);
 const update=lang=>{label.textContent=lang==='bn'?'বিজ্ঞাপন':'Advertisement'};update(document.documentElement.lang);
 const showBookAd=()=>{
  if(!bookOpen||cfg.bookOpen.mode!=='countdown')return;
  const dialog=document.createElement('dialog');if(typeof dialog.showModal!=='function'){section.append(frame);return;}
  dialog.id='bookOpenAd';dialog.className='book-open-ad';dialog.setAttribute('aria-labelledby','bookAdTitle');
  const heading=document.createElement('h2');heading.id='bookAdTitle';
  const countdown=document.createElement('p');countdown.setAttribute('role','status');
  const close=document.createElement('button');close.type='button';close.className='chip';
  const slot=document.createElement('div');slot.className='book-ad-slot';
  dialog.append(heading,slot,countdown,close);section.append(dialog);
  let remaining=5,interval,timeout,finished=false;
  const wording=()=>{const bn=document.documentElement.lang==='bn';heading.textContent=bn?'বিজ্ঞাপন':'Advertisement';countdown.textContent=bn?`${remaining} সেকেন্ড পর বই খুলবে`:`Your book opens in ${remaining} seconds`;close.textContent=bn?'বই খুলুন':'Open book'};
  const finish=()=>{if(finished)return;finished=true;clearInterval(interval);clearTimeout(timeout);dialog.close();dialog.className='book-ad-inline';heading.hidden=true;countdown.hidden=true;close.hidden=true;dialog.show()};
  close.onclick=finish;dialog.addEventListener('cancel',event=>{event.preventDefault();finish()});
  wording();try{dialog.showModal()}catch{dialog.remove();section.append(frame);return}
  slot.append(frame);
  interval=setInterval(()=>{remaining=Math.max(0,remaining-1);wording()},1000);
  timeout=setTimeout(finish,5000);
 };
 document.addEventListener('DOMContentLoaded',()=>{showBookAd();const previous=window.updateAdLabel;window.updateAdLabel=lang=>{previous?.(lang);update(lang)};update(document.documentElement.lang)},{once:true});
})();
