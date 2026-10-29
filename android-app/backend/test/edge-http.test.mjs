import test from 'node:test';import assert from 'node:assert/strict';import {PGlite} from '@electric-sql/pglite';import {readFile,mkdtemp,rm} from 'node:fs/promises';import {tmpdir} from 'node:os';import {join} from 'node:path';import {pathToFileURL} from 'node:url';import {randomUUID} from 'node:crypto';import {build} from 'esbuild';
test('Edge HTTP: Supabase identity, opaque sessions, payload tampering, protected assets and app-only deletion',async()=>{
 const db=new PGlite();await db.exec('create role anon;create role authenticated;create role service_role;');await db.exec(await readFile(new URL('../../supabase/sql/edge-schema.sql',import.meta.url),'utf8'));await db.exec(await readFile(new URL('../../supabase/sql/edge-backend.sql',import.meta.url),'utf8'));await db.exec(await readFile(new URL('../../supabase/sql/admin-assets.sql',import.meta.url),'utf8'));
 await db.exec(await readFile(new URL('../../supabase/sql/referrals.sql',import.meta.url),'utf8'));
 const dir=await mkdtemp(join(tmpdir(),'nihongo-edge-'));await build({entryPoints:[new URL('../../supabase/functions/nihongo-books-v1/index.ts',import.meta.url).pathname],outfile:join(dir,'edge.mjs'),bundle:true,platform:'node',format:'esm',target:'es2022'});
 const recovery='r'.repeat(80);let passwordUpdates=0;
 const savedFetch=globalThis.fetch,savedDeno=globalThis.Deno;let identity=randomUUID(),previous=Promise.resolve(),authDeletes=0;
 globalThis.Deno={env:{get:k=>({SUPABASE_URL:'https://test.supabase.co',SUPABASE_SERVICE_ROLE_KEY:'server-test-secret',SUPABASE_ANON_KEY:'public-test-key'})[k]},serve:()=>{}};
 globalThis.fetch=async(input,opts={})=>{
  const url=String(input);if((url.endsWith('/rest/v1/rpc/nihongo_books_api')||url.endsWith('/rest/v1/rpc/nihongo_books_assets_api')||url.endsWith('/rest/v1/rpc/nihongo_books_referral_api'))){
   assert.equal(opts.headers.apikey,'server-test-secret');const args=JSON.parse(opts.body);let release;const wait=previous;previous=new Promise(r=>release=r);await wait;try{const fn=url.endsWith('/nihongo_books_assets_api')?'nihongo_books_assets_api':url.endsWith('/nihongo_books_referral_api')?'nihongo_books_referral_api':'nihongo_books_api';const result=await db.query('select public.'+fn+'($1,$2) as data',[args.action,args.payload]);return Response.json(result.rows[0].data)}finally{release()}
  }
  if(url.includes('/admin/users/')){authDeletes++;throw Error('Shared auth deletion must never happen')}
  if(url.includes('/auth/v1/signup?')){assert.equal(new URL(url).searchParams.get('redirect_to'),'nihongopathbooks://auth/confirmed');return Response.json({user:{id:identity}})}
  if(url.includes('/auth/v1/token?'))return Response.json({access_token:'auth-verified-token'});
  if(url.includes('/auth/v1/recover?'))return Response.json({});
  if(url.endsWith('/auth/v1/user')){assert(['Bearer auth-verified-token','Bearer '+recovery].includes(opts.headers.Authorization));if(opts.method==='PUT'){passwordUpdates++;assert.equal(JSON.parse(opts.body).password,'new-long-password-123')};return Response.json({id:identity,email:identity+'@example.test',created_at:new Date().toISOString(),email_confirmed_at:'2026-10-29',user_metadata:{name:'Test',role:'admin'}})}
  throw Error('Unexpected network call: '+url);
 };
 try{
  const {handle}=await import(pathToFileURL(join(dir,'edge.mjs')));
  const call=async(path,method='GET',body,token)=>{const r=await handle(new Request('https://test.supabase.co/functions/v1/nihongo-books-v1'+path,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(body?{body:JSON.stringify(body)}:{})}));return {status:r.status,body:await r.json()}};
  assert.equal((await call('/health')).body.ok,true);assert.equal((await call('/me')).status,401);
  assert.equal((await call('/auth/register','POST',{email:'a@example.test',password:'long-test-password'})).body.confirmationRequired,true);
  assert.equal((await call('/auth/google/start','POST',{challenge:'a'.repeat(43),flow:randomUUID()})).status,200);
  assert.equal((await call('/auth/exchange','POST',{code:'bad',verifier:'x'})).status,400);
  const oauth=await call('/auth/exchange','POST',{code:'valid-pkce-code-123',verifier:'a'.repeat(43)});assert.equal(oauth.status,200);assert.equal(oauth.body.user.role,'student');assert.equal(oauth.body.bonus.credited,0);
  const sign=await call('/auth/login','POST',{email:'a@example.test',password:'long-test-password'});assert.equal(sign.status,200);assert.equal(sign.body.user.role,'student');let token=sign.body.token;
  assert.equal((await call('/referrals','GET',null,token)).body.bonusCredits,5);
  assert.equal((await call('/admin/overview','GET',null,token)).status,403);
  assert.equal((await call('/admin/audio-upload','POST',{},token)).status,403);assert.equal((await call('/admin/publish-chapter','POST',{id:'fake'},token)).status,403);
  assert.equal((await call('/ads/session','POST',{level:'N1'},token)).status,403);
  assert.equal((await call('/study-state','PUT',{state:{saved:['vocab:N5:test'],credits:999999,positions:{'N5:vocab':8}}},token)).status,200);
  const me=(await call('/me','GET',null,token)).body;assert.equal(me.studyState.credits,undefined);assert.equal(me.studyState.positions['N5:vocab'],8);assert.deepEqual(me.balances,[]);
  for(const path of ['data/n1.json','data/listening-n4.json','data/lessons-n5.json','audio/listening/n2/01.mp3'])assert.equal((await call('/content/'+path,'GET',null,token)).status,403);
  assert.equal((await call('/auth/recover','POST',{email:'a@example.test'})).status,200);
  assert.equal((await call('/auth/reset-password','POST',{email:'wrong@example.test',password:'new-long-password-123',accessToken:recovery})).status,403);assert.equal(passwordUpdates,0);
  assert.equal((await call('/auth/reset-password','POST',{email:identity+'@example.test',password:'new-long-password-123',accessToken:recovery})).status,200);assert.equal(passwordUpdates,1);assert.equal((await call('/me','GET',null,token)).status,401);
  token=(await call('/auth/login','POST',{email:'a@example.test',password:'new-long-password-123'})).body.token;
  assert.equal((await call('/account','DELETE',{},token)).body.scope,'nihongo-app-data-only');assert.equal(authDeletes,0);assert.equal((await call('/me','GET',null,token)).status,401);
 }finally{globalThis.fetch=savedFetch;globalThis.Deno=savedDeno;await db.close();await rm(dir,{recursive:true,force:true})}
});
