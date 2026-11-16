/* Shared native preferences; the owner-approved Sakura palette is the default. */
window.applyAppAppearance=function(value){
 var dark=value.dark===true,root=document.documentElement,accent=value.accent||'#A03156';
 root.setAttribute('data-app-theme',dark?'dark':'light');
 var colors=dark?{paper:'#18121b',surface:'#281e2a',ink:'#f8e8ef',muted:'#dfb6c8',line:'#684657',pale:'#49303f'}:{paper:'#fff7f9',surface:'#fff2f6',ink:'#4d142d',muted:'#734256',line:'#e7c7d3',pale:'#f8e0e9'};
 Object.keys(colors).forEach(function(k){root.style.setProperty('--'+k,colors[k])});
 root.style.setProperty('--bg',colors.paper);root.style.setProperty('--text',colors.ink);root.style.setProperty('--accent',accent);
 var hex=accent.replace('#',''),n=parseInt(hex,16),r=(n>>16)&255,g=(n>>8)&255,b=n&255;root.style.setProperty('--on-accent',(r*299+g*587+b*114)/1000>155?'#30101e':'#ffffff');
 root.style.setProperty('color-scheme',dark?'dark':'light');
};
try{window.applyAppAppearance(JSON.parse(window.StudyNative.appearance()))}catch(e){window.applyAppAppearance({dark:false})}
