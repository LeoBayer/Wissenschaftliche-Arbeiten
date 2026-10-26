(() => {
'use strict';
const marker=document.getElementById('om-workbook'); if(!marker)return; const root=marker.closest('main'); if(!root)return; root.classList.add('om-workbook');
const key='study-lab-om-tutorium-1-v1', fields=[...root.querySelectorAll('[data-key]')];
const status=document.getElementById('om-save');
function read(){try{return JSON.parse(localStorage.getItem(key)||'{}');}catch{return {};}}
const saved=read();for(const f of fields)if(typeof saved[f.dataset.key]==='string')f.value=saved[f.dataset.key];
function persist(){try{localStorage.setItem(key,JSON.stringify(Object.fromEntries(fields.map(f=>[f.dataset.key,f.value]))));status.textContent='Lokal in diesem Browser gespeichert. Kein Upload, keine Gerätesynchronisation. Wichtige Arbeit zusätzlich exportieren.';}catch{status.textContent='Speichern im Browser nicht verfügbar. Bitte eigene Antworten exportieren, bevor du die Seite verlässt.';}}
function number(s){let t=s.trim().replace(/\s/g,'');if(!t)return NaN;if(t.includes(',')){if(!/^[+-]?(?:\d{1,3}(?:\.\d{3})+|\d+),\d+$/.test(t))return NaN;t=t.replace(/\./g,'').replace(',','.');}else if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(t))return NaN;return Number(t);}
root.addEventListener('input',e=>{if(!e.target.matches('[data-key]'))return;const f=e.target;f.removeAttribute('aria-invalid');f.classList.remove('om-correct','om-wrong');const r=f.parentElement.querySelector('.om-result');if(r)r.textContent='';const sheet=f.closest('.om-sheet');if(sheet)sheet.querySelector('.om-sheet-status').textContent='Eingabe geändert – erneut prüfen.';persist();});
for(const btn of root.querySelectorAll('[data-check]'))btn.addEventListener('click',()=>{
 const sheet=btn.closest('.om-sheet');let correct=0,empty=0,wrong=0;
 for(const f of sheet.querySelectorAll('[data-answer]')){const r=f.parentElement.querySelector('.om-result'),v=number(f.value),expected=Number(f.dataset.answer);f.classList.remove('om-correct','om-wrong');
 if(!f.value.trim()){empty++;r.textContent='Noch offen';f.removeAttribute('aria-invalid');}
 else if(!Number.isFinite(v)){wrong++;r.textContent='Zahl ungültig';f.setAttribute('aria-invalid','true');f.classList.add('om-wrong');}
 else if(Math.abs(v-expected)<=0.011){correct++;r.textContent='Richtig';f.setAttribute('aria-invalid','false');f.classList.add('om-correct');}
 else{wrong++;r.textContent='Noch nicht richtig';f.setAttribute('aria-invalid','true');f.classList.add('om-wrong');}}
 sheet.querySelector('.om-sheet-status').textContent=`${correct} richtig · ${wrong} zu prüfen · ${empty} offen. Toleranz: 0,011 für auf zwei Dezimalstellen gerundete Werte. Eigene Eingaben bleiben unverändert.`;
});
document.getElementById('om-export').addEventListener('click',()=>{const data={titel:'OM Tutorium 1',stand:new Date().toISOString(),antworten:Object.fromEntries(fields.map(f=>[f.dataset.key,f.value]))};const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='om-tutorium-1-antworten.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);});
document.getElementById('om-reset').addEventListener('click',()=>{if(!confirm('Alle eigenen Antworten dieses Tutoriums in diesem Browser löschen?'))return;for(const f of fields){f.value='';f.removeAttribute('aria-invalid');f.classList.remove('om-correct','om-wrong');}for(const r of root.querySelectorAll('.om-result,.om-sheet-status'))r.textContent='';persist();});
function fit(xs,ys,log){const zs=xs.map(x=>log?Math.log(x):x),n=xs.length,sx=zs.reduce((a,b)=>a+b,0),sy=ys.reduce((a,b)=>a+b,0),sxx=zs.reduce((a,b)=>a+b*b,0),sxy=zs.reduce((a,b,i)=>a+b*ys[i],0),b=(n*sxy-sx*sy)/(n*sxx-sx*sx),a=(sy-b*sx)/n;return x=>a+b*(log?Math.log(x):x);}
function chart(title,xs,ys,maxx,maxy,log){const w=650,h=340,L=70,R=20,T=35,B=65;const X=x=>L+x/maxx*(w-L-R),Y=y=>h-B-y/maxy*(h-T-B);let s=`<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${title}"><title>${title}</title><text x="${L}" y="20">${title}</text><path d="M${L} ${T}V${h-B}H${w-R}" class="om-axis"/>`;
for(let i=0;i<=5;i++){const x=maxx*i/5,y=maxy*i/5;s+=`<text x="${X(x)}" y="${h-B+22}" text-anchor="middle">${x}</text><text x="${L-10}" y="${Y(y)+4}" text-anchor="end">${y}</text>`;}
s+=`<text x="${w/2}" y="${h-14}" text-anchor="middle">${log?'Marketingbudget [1.000 €]':'Installierte Pressen [Stück]'}</text><text x="${L+10}" y="${T+18}">${log?'Nachfrage [Stück]':'Wartung [h/Quartal]'}</text>`;
for(const [idx,lg] of (log?[false,true]:[false]).entries()){const f=fit(xs,ys,lg);const pts=[];for(let i=0;i<=120;i++){const x=log?30+(maxx-30)*i/120:maxx*i/120,y=f(x);if(y>=0&&y<=maxy)pts.push(`${X(x)},${Y(y)}`);}s+=`<polyline points="${pts.join(' ')}" class="om-line ${idx?'om-log':''}"/>`;}
xs.forEach((x,i)=>s+=`<circle cx="${X(x)}" cy="${Y(ys[i])}" r="5" class="om-dot"><title>x=${x}, y=${ys[i]}</title></circle>`);s+='</svg>';return `<figure>${s}<figcaption>Punkte: Ausgangsdaten. Durchgezogen: lineare Regression.${log?' Gestrichelt: logarithmische Regression; Bereich rechts von 650 ist Extrapolation.':''}</figcaption></figure>`;}
document.getElementById('om-charts').innerHTML=chart('Wartung und installierte Basis',[5,15,30,50,100,150,200],[45,68,109,141,262,320,444],220,500,false)+chart('Marketing: Modellformen vergleichen',[30,150,240,370,500,650],[35,265,355,417,451,503],1000,850,true);
})();
