/* Exactly one account-approved display unit. No Popunder, refresh or book gate. */
(()=>{'use strict';const cfg=window.NIHONGO_ADSTERRA;if(!cfg?.enabled)return;
 const desktop=matchMedia('(min-width: 768px)').matches,u=desktop?cfg.desktop:cfg.mobile;
 if(!u||!/^\w{32}$/.test(u.key)||u.src!==`https://bauval.org/22/${u.key}`)return;
 if(!((u.width===320&&u.height===50)||(u.width===300&&u.height===250)))return;
 const section=document.createElement('section');section.id='adsterraPlacement';section.className='ad-panel adsterra-panel';section.setAttribute('aria-label','Advertisement');const label=document.createElement('small');section.append(label);
 const frame=document.createElement('iframe');frame.title='Advertisement';frame.src=desktop?'adsterra-banner-desktop.html':'adsterra-banner-mobile.html';frame.width=u.width;frame.height=u.height;frame.loading='lazy';frame.style.cssText='display:block;margin:12px auto;border:0;max-width:100%';section.append(frame);
 document.querySelector('main')?.insertAdjacentElement('afterend',section);
 const update=lang=>{label.textContent=lang==='bn'?'বিজ্ঞাপন':'Advertisement'};update(document.documentElement.lang);
 document.addEventListener('DOMContentLoaded',()=>{const previous=window.updateAdLabel;window.updateAdLabel=lang=>{previous?.(lang);update(lang)};update(document.documentElement.lang)},{once:true});
})();
