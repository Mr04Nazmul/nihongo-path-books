const {test}=require('node:test');const assert=require('node:assert/strict');const vm=require('node:vm');const fs=require('node:fs');
function setup(manifest={},rejectAudio=false){
 const nodes=[],calls=[],timers=new Map();let index=0;
 class Node{constructor(tag='button'){this.tag=tag;this.textContent='▷ Listen';this.isConnected=true;this.attrs={};this.parentElement={querySelector:()=>null};}setAttribute(k,v){this.attrs[k]=v}removeAttribute(k){delete this.attrs[k]}insertAdjacentElement(_,n){nodes.push(n)}append(n){nodes.push(n)}remove(){}get classList(){return{toggle(){}}}}
 class Audio extends Node{constructor(){super('audio');this.currentTime=0;this.paused=true}play(){calls.push(['audio',this.src]);if(rejectAudio)return Promise.reject(Error('blocked'));this.paused=false;this.onplaying?.();return Promise.resolve()}pause(){this.paused=true;calls.push(['pause'])}}
 const ja={lang:'ja-JP',name:'Japanese',localService:true},en={lang:'en-US'};
 const synth={paused:false,getVoices:()=>[en,ja],addEventListener(){},speak(u){calls.push(['speak',u])},cancel(){calls.push(['cancel'])},resume(){calls.push(['resume'])}};
 const document={documentElement:{lang:'en'},createElement:t=>t==='audio'?new Audio():new Node(t),querySelector:()=>new Node('main'),addEventListener(){}};
 const window={speechSynthesis:synth,SpeechSynthesisUtterance:class{constructor(text){this.text=text}}};
 const context={window,document,SpeechSynthesisUtterance:window.SpeechSynthesisUtterance,fetch:async()=>({ok:true,json:async()=>manifest}),setTimeout:f=>{timers.set(++index,f);return index},clearTimeout:id=>timers.delete(id),console};vm.runInNewContext(fs.readFileSync('dist/speech.js','utf8'),context);
 return {service:window.NihongoSpeech,synth,calls,nodes,timers,button:new Node(),ja};
}
test('native speech starts synchronously from the tap with a Japanese voice',()=>{const s=setup();s.service.play('日本語',s.button);assert.equal(s.calls[0][0],'speak');const u=s.calls[0][1];assert.equal(u.voice,s.ja);assert.equal(u.lang,'ja-JP');assert.equal(u.volume,1);u.onstart();assert.match(s.button.textContent,/Playing/);u.onend();assert.equal(s.button.textContent,'▷ Listen')});
test('first tap does not cancel an idle Safari speech queue',()=>{const s=setup();s.service.play('こんにちは',s.button);assert.equal(s.calls.filter(x=>x[0]==='cancel').length,0)});
test('silent failure surfaces actionable feedback',()=>{const s=setup();s.service.play('日本語',s.button);[...s.timers.values()][0]();assert(s.nodes.some(x=>/did not start/.test(x.textContent)));assert.equal(s.button.attrs['aria-pressed'],'false')});
test('daily word plays a real clip through the media channel',async()=>{const s=setup({'あんな':'anna.mp3'});await s.service.ready;s.service.play('あんな',s.button);assert.deepEqual(s.calls[0],['audio','audio/anna.mp3']);assert(!s.calls.some(x=>x[0]==='speak'));s.service.play('あんな',s.button);assert(s.calls.some(x=>x[0]==='pause'))});
test('blocked media presents native playback controls instead of failing silently',async()=>{const s=setup({'あんな':'anna.mp3'},true);await s.service.ready;s.service.play('あんな',s.button);await Promise.resolve();assert(s.nodes.some(x=>x.tag==='audio'&&x.controls===true));assert(s.nodes.some(x=>/audio player/.test(x.textContent)))});
