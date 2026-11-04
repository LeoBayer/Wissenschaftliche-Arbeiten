(() => {
'use strict';
const marker=document.getElementById('ct-workbook'); if(!marker)return; const root=marker.closest('main'); if(!root)return; root.classList.add('ct-workbook');
const key='study-lab-controlling-tutorium-2-v1', fields=[...root.querySelectorAll('[data-key]')];
const status=document.getElementById('ct-save');
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
document.getElementById('ct-export').addEventListener('click',()=>{const data={titel:'Controlling Tutorium 2',stand:new Date().toISOString(),antworten:Object.fromEntries(fields.map(f=>[f.dataset.key,f.value]))};const u=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='controlling-tutorium-2-antworten.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);});
document.getElementById('ct-reset').addEventListener('click',()=>{if(!confirm('Alle eigenen Antworten dieses Tutoriums in diesem Browser löschen?'))return;for(const f of fields){f.value='';f.removeAttribute('aria-invalid');f.classList.remove('om-correct','om-wrong');}for(const r of root.querySelectorAll('.om-result,.om-sheet-status'))r.textContent='';persist();});
})();
