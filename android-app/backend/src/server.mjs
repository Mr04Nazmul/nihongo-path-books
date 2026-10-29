import http from 'node:http';import {readFile} from 'node:fs/promises';import {Store,Fault} from './store.mjs';import {login,authenticate,hashToken} from './auth.mjs';import {verifyCallback} from './ssv.mjs';import {protectedFile} from './content.mjs';
const store=new Store(process.env.DATABASE_URL),root=process.env.CONTENT_ROOT||'../../dist',limits=new Map();
function rate(key){const now=Date.now(),v=limits.get(key)||{at:now,n:0};if(now-v.at>60000){v.at=now;v.n=0}if(++v.n>15)throw new Fault(429,'Please wait a minute and try again');limits.set(key,v)}
setInterval(()=>{for(const[k,v]of limits)if(Date.now()-v.at>120000)limits.delete(k)},60000).unref();
async function body(req){let s='';for await(const chunk of req){s+=chunk;if(s.length>16384)throw new Fault(413,'Request too large')}try{return JSON.parse(s||'{}')}catch{throw new Fault(400,'Invalid JSON')}}
function uuid(v){if(!/^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(v||''))throw new Fault(400,'Valid request ID required');return v}
const server=http.createServer(async(req,res)=>{
 res.setHeader('Cache-Control','no-store, private');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');const send=(s,b)=>{res.writeHead(s,{'Content-Type':'application/json; charset=utf-8'});res.end(JSON.stringify(b))};
 try{const route=new URL(req.url,'http://localhost').pathname;
 if(route==='/health'){await store.tx(c=>c.query('select 1'));return send(200,{ok:true})}
 if(['/admin','/admin.js','/admin.css'].includes(route)&&req.method==='GET'){res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'");const file=route==='/admin'?'/admin.html':route;res.writeHead(200,{'Content-Type':file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'text/html; charset=utf-8'});return res.end(await readFile(new URL('../public'+file,import.meta.url)))}
 if(route==='/ssv'&&req.method==='GET'){const p=await verifyCallback(req.url.split('?')[1]||'',(process.env.ADMOB_ALLOWED_UNITS||'ca-app-pub-3940256099942544/5224354917').split(','));try{return send(200,await store.reward(p))}catch(e){await store.event(null,'suspicious_reward',{reason:e.message,transaction:p.transaction_id}).catch(()=>{});throw e}}
 if(['/auth/login','/auth/register'].includes(route)&&req.method==='POST'){rate(req.socket.remoteAddress);return send(200,await login(store,await body(req),route.endsWith('register')))}
 const user=await authenticate(store,req.headers.authorization);
 if(route==='/me'&&req.method==='GET')return send(200,{user,...await store.snapshot(user.id)});
 if(route==='/auth/logout'&&req.method==='POST'){await store.tx(c=>c.query('delete from books.sessions where token_hash=$1',[hashToken(req.headers.authorization.replace('Bearer ',''))]));return send(200,{ok:true})}
 if(route==='/profile'&&req.method==='PATCH'){const b=await body(req);await store.tx(c=>c.query('update books.users set name=$2 where id=$1',[user.id,String(b.name||'').slice(0,100)]));return send(200,{ok:true})}
 if(route==='/account'&&req.method==='DELETE'){await store.tx(c=>c.query('delete from books.users where id=$1',[user.id]));return send(200,{ok:true})}
 if(route==='/ads/session'&&req.method==='POST'){if(process.env.REWARDS_ENABLED==='false')throw new Fault(503,'Ads paused. Credits are safe.');return send(200,await store.startAd(user.id,(await body(req)).level))}
 if(route==='/redeem'&&req.method==='POST'){const b=await body(req);return send(200,await store.redeem(user.id,b.tierId,uuid(b.requestId)))}
 if(route.startsWith('/content/')&&req.method==='GET'){const f=await protectedFile(root,decodeURIComponent(route.slice(9)),user,store);await store.event(user.id,'content_open',{level:f.level}).catch(()=>{});res.writeHead(200,{'Content-Type':f.type,'Accept-Ranges':'none'});return res.end(f.body)}
 if(route.startsWith('/admin/')){
 if(user.role!=='admin')throw new Fault(403,'Administrator access required');
 if(route==='/admin/overview'&&req.method==='GET')return send(200,await store.tx(async c=>({tiers:(await c.query('select * from books.tiers order by level desc,seconds')).rows,config:(await c.query('select * from books.config')).rows[0],counts:(await c.query("select (select count(*) from books.users) as users,(select count(*) from books.rewards) as verified_ads,(select coalesce(sum(credits),0) from books.rewards) as issued,(select coalesce(sum(credits),0) from books.redemptions) as redeemed,(select count(*) from books.unlocks where expires_at>now()) as active_unlocks")).rows[0],events:(await c.query('select kind,detail,created_at from books.events order by id desc limit 100')).rows})));
 if(route==='/admin/config'&&req.method==='PATCH'){const b=await body(req);if(typeof b.rewardsEnabled!=='boolean')throw new Fault(400,'Invalid config');await store.tx(c=>c.query('update books.config set rewards_enabled=$1',[b.rewardsEnabled]));await store.event(user.id,'admin_config',b);return send(200,{ok:true})}
 if(route==='/admin/tier'&&req.method==='PATCH'){const b=await body(req);if(!Number.isInteger(b.credits)||b.credits<1||b.credits>1000||!Number.isInteger(b.seconds)||b.seconds<1||b.seconds>2592000||typeof b.enabled!=='boolean')throw new Fault(400,'Invalid tier');const r=await store.tx(c=>c.query('update books.tiers set credits=$2,seconds=$3,enabled=$4 where id=$1 returning *',[b.id,b.credits,b.seconds,b.enabled]));if(!r.rowCount)throw new Fault(404,'Tier not found');await store.event(user.id,'admin_tier',b);return send(200,r.rows[0])}
 }
 throw new Fault(404,'Route not found');
 }catch(e){if(!e.status)console.error('Request failed:',e.code||e.name);send(e.status||500,{error:e.status?e.message:'Service unavailable. Your credits are safe.'})}
});server.requestTimeout=15000;server.headersTimeout=10000;server.listen(Number(process.env.PORT||8080),'0.0.0.0',()=>console.log('Books API listening'));
