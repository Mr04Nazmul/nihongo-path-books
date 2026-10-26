/* Native speech stays inside the original tap. Media clips use the media channel. */
(function () {
  'use strict';
  const copy = {
    bn: { loading:'অডিও প্রস্তুত হচ্ছে…', playing:'চলছে… থামাতে চাপুন', done:'শোনা শেষ', stopped:'অডিও বন্ধ', failed:'অডিও শুরু হয়নি। ফোনের মিডিয়া ভলিউম বাড়িয়ে আবার চাপুন। অ্যাপের ভেতরে না চললে Safari-তে লিংকটি খুলুন।', unavailable:'এই ব্রাউজারে Japanese voice পাওয়া যায়নি। Safari-তে খুলুন; প্রয়োজনে iPhone Settings → Accessibility → Read & Speak / Spoken Content → Voices থেকে Japanese voice ডাউনলোড করুন।', retry:'নিচের অডিও প্লেয়ারের Play চাপুন।' },
    en: { loading:'Preparing audio…', playing:'Playing… tap to stop', done:'Finished', stopped:'Audio stopped', failed:'Audio did not start. Turn up media volume and tap again. If this in-app browser blocks speech, open the link in Safari.', unavailable:'No Japanese voice is available here. Open in Safari. If needed, download a Japanese voice in iPhone Settings → Accessibility → Read & Speak / Spoken Content → Voices.', retry:'Press Play on the audio player below.' }
  };
  const synth = window.speechSynthesis;
  let voices = [], active = null, media = null, serial = 0, manifest = {};
  const refresh = () => { try { voices = synth ? synth.getVoices() : []; } catch (_) { voices = []; } };
  refresh();
  if (synth?.addEventListener) synth.addEventListener('voiceschanged', refresh);
  const manifestReady = fetch('audio/manifest.json').then(r => r.ok ? r.json() : {}).then(data => { manifest = data; }).catch(() => {});
  const lang = () => copy[document.documentElement.lang] || copy.en;
  function status(button, message, error) {
    let node = button?.parentElement?.querySelector('.speech-status');
    if (!node) {
      node = document.createElement('p'); node.className = 'speech-status';
      node.setAttribute('role','status'); node.setAttribute('aria-live','polite');
      if (button) button.insertAdjacentElement('afterend', node); else document.querySelector('main')?.append(node);
    }
    node.textContent = message; node.classList.toggle('speech-error', !!error);
  }
  function finish(id, message, error) {
    if (!active || active.id !== id) return;
    clearTimeout(active.timer);
    const button = active.button;
    if (button?.isConnected) { button.textContent = active.label; button.setAttribute('aria-pressed','false'); button.removeAttribute('aria-busy'); }
    if (message) status(button,message,error);
    active = null;
  }
  function stop() {
    if (media) { media.pause(); media.remove(); media = null; }
    if (!active) return;
    const old = active; active = null; clearTimeout(old.timer);
    if (old.audio) { old.audio.pause(); old.audio.currentTime = 0; }
    if (old.utterance && synth) synth.cancel();
    if (old.button?.isConnected) { status(old.button,lang().stopped); old.button.textContent = old.label; old.button.setAttribute('aria-pressed','false'); old.button.removeAttribute('aria-busy'); }
  }
  function play(text, button) {
    text = String(text || '').trim(); if (!text) return;
    const previous = active;
    if (previous?.button === button && previous?.text === text) { stop(); status(button,lang().stopped); return; }
    stop(); refresh();
    const id = ++serial;
    active = { id, text, button, label:button?.textContent || '▷ Listen', utterance:null, audio:null, timer:null };
    button?.setAttribute('aria-busy','true'); button?.setAttribute('aria-pressed','true');
    status(button,lang().loading);
    const path = manifest[text];
    if (path) {
      const audio = document.createElement('audio'); audio.preload = 'auto'; audio.src = 'audio/' + path;
      audio.setAttribute('playsinline',''); active.audio = audio; media = audio;
      audio.onplaying = () => { if(active?.id===id){clearTimeout(active.timer);button && (button.textContent=lang().playing);status(button,'');button?.removeAttribute('aria-busy');} };
      audio.onended = () => finish(id,lang().done);
      const showControls = () => {
        if (active?.id !== id) return;
        audio.controls = true; audio.className='speech-player';
        button?.insertAdjacentElement('afterend',audio);
        finish(id,lang().retry,true);
      };
      audio.onerror = showControls;
      active.timer = setTimeout(showControls,8000);
      try { const playing = audio.play(); playing?.catch(showControls); } catch (_) { showControls(); }
      return;
    }
    if (!synth || typeof window.SpeechSynthesisUtterance !== 'function') { finish(id,lang().unavailable,true); return; }
    const japanese = voices.filter(v => /^ja(?:[-_]|$)/i.test(v.lang));
    const voice = japanese.find(v => v.localService) || japanese[0];
    const utterance = new SpeechSynthesisUtterance(text);
    // Keep this strong reference until end/error; some WebKit builds drop unretained utterances.
    active.utterance = utterance;
    utterance.lang = voice?.lang || 'ja-JP'; if (voice) utterance.voice = voice;
    utterance.rate = 0.85; utterance.pitch = 1; utterance.volume = 1;
    utterance.onstart = () => { if(active?.id===id){clearTimeout(active.timer);button && (button.textContent=lang().playing);status(button,'');button?.removeAttribute('aria-busy');} };
    utterance.onend = () => finish(id,lang().done);
    utterance.onerror = event => { if(!['canceled','interrupted'].includes(event.error))finish(id,event.error==='language-unavailable'||event.error==='voice-unavailable'?lang().unavailable:lang().failed,true);else finish(id,''); };
    active.timer = setTimeout(() => { if(active?.id===id){ const message = japanese.length ? lang().failed : lang().unavailable;finish(id,message,true);synth.cancel(); } },3000);
    try { if(synth.paused) synth.resume(); synth.speak(utterance); } catch (_) { finish(id,lang().failed,true); }
  }
  window.NihongoSpeech = { play, stop, ready:manifestReady };
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
})();
