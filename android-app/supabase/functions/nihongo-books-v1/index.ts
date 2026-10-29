import {Fault} from './errors.ts';
import {verifyCallback} from './ssv.mjs';
import {assets} from './assets.ts';
const project=Deno.env.get('SUPABASE_URL')!;
const service=Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const publicKey=Deno.env.get('SUPABASE_ANON_KEY')!;
const headers={'Cache-Control':'no-store, private','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'};
const json=(data:unknown,status=200)=>new Response(JSON.stringify(data),{status,headers:{...headers,'Content-Type':'application/json; charset=utf-8'}});
export async function hash(value:string){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)))].map(n=>n.toString(16).padStart(2,'0')).join('')}
async function rpc(action:string,payload:Record<string,unknown>={}){
 const r=await fetch(project+'/rest/v1/rpc/nihongo_books_api',{method:'POST',headers:{apikey:service,Authorization:'Bearer '+service,'Content-Type':'application/json'},body:JSON.stringify({action,payload}),signal:AbortSignal.timeout(15000)});
 if(!r.ok){console.error('Books RPC unavailable',r.status);throw new Fault(503,'Study service unavailable. Your credits are safe.')}
 const b=await r.json();if(b.error)throw new Fault(b.status||400,b.error);return b;
}
async function body(req:Request){const b=await req.text();if(new TextEncoder().encode(b).length>200000)throw new Fault(413,'Request too large');try{const d=JSON.parse(b||'{}');if(!d||typeof d!=='object'||Array.isArray(d))throw Error();return d}catch{throw new Fault(400,'Invalid JSON')}}
async function auth(path:string,method:string,b:unknown){const r=await fetch(project+'/auth/v1'+path,{method,headers:{apikey:publicKey,'Content-Type':'application/json'},body:JSON.stringify(b),redirect:'error',signal:AbortSignal.timeout(15000)});const d=await r.json();if(!r.ok)throw new Fault(r.status>=500?503:400,'Authentication failed. Check email confirmation and sign-in details.');return d}
function cleanState(s:any){if(!s||typeof s!=='object'||Array.isArray(s))throw new Fault(400,'Invalid study state');const c:any={positions:{}};for(const k of ['saved','learned']){if(s[k]&&!Array.isArray(s[k]))throw new Fault(400,'Invalid bookmarks');c[k]=(s[k]||[]).filter((v:unknown)=>typeof v==='string'&&v.length<200);if(c[k].length>2000)throw new Fault(400,'Bookmark limit reached; export your progress before clearing entries')};for(const k of ['lang','level','dark','bookMotion','readingSize'])if(['string','boolean'].includes(typeof s[k]))c[k]=s[k];for(const[k,v]of Object.entries(s.positions||{}))if(/^N[2-5]:(vocab|grammar|kanji)$/.test(k)&&Number.isInteger(v)&&Number(v)>=0&&Number(v)<100000)c.positions[k]=v;return c}
function levelOf(path:string){const m=/^(?:data\/(?:lessons-|owner-|listening-)?|pdfs\/(?:jlpt-)?|audio\/(?:listening\/)?)(n[1-5])(?:[./-])/i.exec(path);return m?.[1].toUpperCase()}
export async function handle(req:Request):Promise<Response>{
 try{
  const url=new URL(req.url),marker='/nihongo-books-v1',start=url.pathname.indexOf(marker),route=start>=0?url.pathname.slice(start+marker.length)||'/':url.pathname;
  if(route==='/health'&&req.method==='GET')return json(await rpc('health'));
  if(req.method==='GET'&&['/admin','/admin.js','/admin.css','/privacy','/support','/delete-account'].includes(route)){
   const file=route==='/admin'?'admin.html':route.slice(1)+(route.includes('.')?'':'.html');return new Response(assets[file],{headers:{...headers,'Content-Type':file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'"}});
  }
  if(route==='/ssv'&&req.method==='GET'){
   const p=await verifyCallback(url.search.slice(1),(Deno.env.get('ADMOB_ALLOWED_UNITS')||'ca-app-pub-3940256099942544/5224354917').split(','));
   if(p.verificationProbe)return json({verified:true,test:true,credited:0});return json(await rpc('reward',p));
  }
  if(['/auth/register','/auth/login','/auth/recover','/auth/reset-password'].includes(route)&&req.method==='POST'){
   const ip=req.headers.get('x-forwarded-for')||'unknown';await rpc('rate',{key:await hash(ip)});const b=await body(req),email=String(b.email||'').trim().toLowerCase();
   if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||email.length>254)throw new Fault(400,'Use a valid email');
   if(route==='/auth/reset-password'){
    const password=String(b.password||''),accessToken=String(b.accessToken||'');if(password.length<10||password.length>128||accessToken.length<40||accessToken.length>8192)throw new Fault(400,'Use a valid recovery link and a 10–128 character password');
    const check=await fetch(project+'/auth/v1/user',{headers:{apikey:publicKey,Authorization:'Bearer '+accessToken},signal:AbortSignal.timeout(15000)});if(!check.ok)throw new Fault(401,'Recovery link expired. Request a new email.');const verified=await check.json();if(String(verified.email).toLowerCase()!==email)throw new Fault(403,'Recovery email does not match this account');
    await rpc('revoke_identity',{verifiedUserId:verified.id});
    const updated=await fetch(project+'/auth/v1/user',{method:'PUT',headers:{apikey:publicKey,Authorization:'Bearer '+accessToken,'Content-Type':'application/json'},body:JSON.stringify({password}),signal:AbortSignal.timeout(15000)});if(!updated.ok)throw new Fault(400,'Password could not be changed. Request a new recovery link.');
    return json({ok:true,message:'Password changed. Sign in again on your Nihongo devices.'});
   }
   if(route==='/auth/recover'){await auth('/recover?redirect_to='+encodeURIComponent('nihongopathbooks://auth/recovery'),'POST',{email});return json({ok:true,message:'If this account exists, check the recovery email. Recovery uses the Supabase project account.'})}
   const password=String(b.password||'');if(password.length<10||password.length>128)throw new Fault(400,'Use a 10–128 character password');
   const d=await auth(route.endsWith('register')?'/signup':'/token?grant_type=password','POST',{email,password,...(route.endsWith('register')?{data:{name:String(b.name||'').slice(0,100)}}:{})});
   if(!d.access_token)throw new Fault(409,'Check your email to confirm your account, then sign in.');
   const verification=await fetch(project+'/auth/v1/user',{headers:{apikey:publicKey,Authorization:'Bearer '+d.access_token},signal:AbortSignal.timeout(15000)});if(!verification.ok)throw new Fault(401,'Sign in again');const u=await verification.json();if(!u.id||!u.email_confirmed_at)throw new Fault(403,'Confirm your email first');
   const bytes=crypto.getRandomValues(new Uint8Array(32)),token=btoa(String.fromCharCode(...bytes)).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
   const result=await rpc('login',{id:u.id,email:u.email,name:u.user_metadata?.name||'',confirmed:true,sessionHash:await hash(token)});return json({...result,token});
  }
  const token=req.headers.get('Authorization')?.replace(/^Bearer /,'')||'';if(!/^[\w-]{43}$/.test(token))throw new Fault(401,'Please sign in');const tokenHash=await hash(token);
  const me=await rpc('authenticate',{tokenHash});
  if(route==='/me'&&req.method==='GET')return json(await rpc('snapshot',{tokenHash}));
  const mapped:Record<string,[string,string]>={'/auth/logout':['POST','logout'],'/auth/logout-all':['POST','logout_all'],'/account':['DELETE','delete_account'],'/profile':['PATCH','profile'],'/study-state':['PUT','state'],'/ads/session':['POST','ad_session'],'/redeem':['POST','redeem'],'/admin/overview':['GET','admin_overview'],'/admin/level':['PATCH','admin_level'],'/admin/tier':['PATCH','admin_tier'],'/admin/config':['PATCH','admin_config'],'/admin/chapter':['PUT','admin_chapter'],'/admin/audio':['PUT','admin_audio']};
  if(mapped[route]&&mapped[route][0]===req.method){
   const b=req.method==='GET'?{}:await body(req);if(mapped[route][1]==='state')b.state=cleanState(b.state);
   if(route==='/redeem'&&!/^[a-f0-9-]{36}$/i.test(b.requestId||''))throw new Fault(400,'Valid request ID required');
   return json(await rpc(mapped[route][1],{...b,tokenHash}));
  }
  if(route.startsWith('/content/')&&req.method==='GET'){
   const path=decodeURIComponent(route.slice(9));if(!/^[\w/.-]+$/.test(path)||path.includes('..')||path.includes('\\'))throw new Fault(400,'Invalid path');const level=levelOf(path);
   if(!level||level==='N1'||(/^(audio\/|data\/listening-)/.test(path)&&level!=='N5'))throw new Fault(403,'Unavailable in this release');
   const allowed=await rpc('allowed',{tokenHash,level});if(!allowed.allowed)throw new Fault(403,'Unlock this level in the Reward Center');
   const source=await fetch('https://devnazu.online/'+path,{redirect:'error',signal:AbortSignal.timeout(45000)});
   if(!source.ok)throw new Fault(source.status===404?404:503,'This material is unavailable');
   if(Number(source.headers.get('content-length')||0)>20000000){await source.body?.cancel();throw new Fault(413,'Material too large')}
   await rpc('event',{tokenHash,kind:'content_open',detail:{level}});
   return new Response(source.body,{headers:{...headers,'Content-Type':source.headers.get('content-type')||'application/octet-stream','Accept-Ranges':'none'}});
  }
  throw new Fault(404,'Route not found');
 }catch(e){if(e instanceof Fault)return json({error:e.message},e.status);console.error('Books edge error',e instanceof Error?e.name:'unknown');return json({error:'Service unavailable. Your credits are safe.'},503)}
}
Deno.serve(handle);
