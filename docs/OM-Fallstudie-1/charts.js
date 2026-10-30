(async()=>{
'use strict';
const el=id=>document.getElementById(id), fmt=(x,n=1)=>new Intl.NumberFormat('de-DE',{maximumFractionDigits:n,minimumFractionDigits:n}).format(x);
if(!el('annual-plot')&&!el('metric-plot'))return;
try{
const response=await fetch('charts-data.json');if(!response.ok)throw Error('Diagrammdaten nicht erreichbar');const data=await response.json(),methods=data.Korrektur.methods;
const grid=(max,ticks,left=70,bottom=300,width=640,height=240)=>Array.from({length:ticks+1},(_,i)=>{const v=max*i/ticks,y=bottom-height*i/ticks;return `<line class="grid" x1="${left}" x2="${left+width}" y1="${y}" y2="${y}"/><text x="${left-12}" y="${y+5}" text-anchor="end">${fmt(v,0)}</text>`;}).join('');
function annual(){
const mode=el('annual-mode').value,ys=data[mode].annuals,x=[0,1,2,3],mean=ys.reduce((a,b)=>a+b)/4,b=ys.reduce((sum,y,i)=>sum+(i-1.5)*(y-mean),0)/5,a=mean-b*1.5,pred=a+4*b;
const px=i=>80+i*150,py=y=>300-(y-3000)/2600*230;
let svg='<text x="70" y="23">Räder · Jahresmengen</text>';
for(let v=3000;v<=5500;v+=500)svg+=`<line class="grid" x1="80" x2="700" y1="${py(v)}" y2="${py(v)}"/><text x="65" y="${py(v)+5}" text-anchor="end">${fmt(v,0)}</text>`;
svg+=`<polyline points="${ys.map((y,i)=>`${px(i)},${py(y)}`).join(' ')}" fill="none" stroke="#64849b" stroke-width="3"/><line class="accent" x1="80" y1="${py(a)}" x2="680" y2="${py(pred)}" stroke-width="3" stroke-dasharray="8 6"/>`;
[...ys,pred].forEach((y,i)=>{svg+=`<circle cx="${px(i)}" cy="${py(y)}" r="6" fill="${i===4?'#a52c40':'#64849b'}"/><text x="${px(i)}" y="${py(y)-15}" text-anchor="middle">${fmt(y,1)}</text><text x="${px(i)}" y="328" text-anchor="middle">${2023+i}${i===4?'*':''}</text>`;});
svg+='<text x="80" y="354">* Prognose · durchgezogen: Ist · gestrichelt: Trend · Mengenachse ab 3.000</text>';el('annual-plot').innerHTML=svg;
el('annual-caption').textContent=`${mode==='Korrektur'?'Mit':'Ohne'} Korrektur: Steigung ${fmt(b)} Räder pro Jahr, Basisprognose ${fmt(pred)} Räder. Der Zusatzauftrag ist nicht enthalten.`;
}
function season(){
const flat=el('season-mode').value==='flat',total=5122.5,values=flat?Array(12).fill(total/12):methods['Jahrestrend + Saisonanteile'].months,months=['Okt','Nov','Dez','Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep'];
let svg='<text x="70" y="23">Räder pro Monat · Planjahr Oktober 2026 bis September 2027</text>'+grid(800,4);
values.forEach((v,i)=>{const x=80+i*52,y=300-v/800*240;svg+=`<rect x="${x}" y="${y}" width="32" height="${300-y}" rx="3" fill="${flat?'#64849b':'#a52c40'}"><title>${months[i]}: ${fmt(v,2)} Räder</title></rect><text x="${x+16}" y="${y-8}" text-anchor="middle" style="font-size:12px">${fmt(v,0)}</text><text x="${x+16}" y="325" text-anchor="middle">${months[i]}</text>`;});
el('season-plot').innerHTML=svg;el('season-caption').textContent=`${flat?'Gleichmäßige':'Saisonale'} Verteilung: insgesamt ${fmt(values.reduce((a,b)=>a+b),1)} Räder. Werte sind Erwartungsmengen, keine festgelegten Bestelllose; ohne Zusatzauftrag.`;
el('season-table').innerHTML='<table><thead><tr><th>Monat</th><th>Basisprognose (Räder)</th></tr></thead><tbody>'+values.map((v,i)=>`<tr><td>${months[i]} ${i<3?'2026':'2027'}</td><td>${fmt(v,2)}</td></tr>`).join('')+'</tbody></table>';
}
function metric(){
const key=el('metric-mode').value,entries=Object.entries(methods),max=Math.max(...entries.map(([,v])=>v[key]))*1.2,isForecast=key==='annual_forecast',unit=key==='MSE'?'Räder²':'Räder';let svg=`<text x="20" y="28">${isForecast?'Basisprognose 2027':'Rücktestfehler'} · ${unit} · Balken beginnen bei null</text>`;
for(let i=0;i<=4;i++){const x=270+i*100;svg+=`<line class="grid" x1="${x}" x2="${x}" y1="50" y2="300"/><text x="${x}" y="330" text-anchor="middle">${fmt(max*i/4,0)}</text>`;}
entries.forEach(([name,v],i)=>{const y=68+i*61,len=v[key]/max*400,color=name.startsWith('Jahrestrend')?'#a52c40':'#64849b';svg+=`<text x="15" y="${y+22}">${name}</text><rect x="270" y="${y}" width="${len}" height="32" rx="4" fill="${color}"><title>${name}: ${fmt(v[key],2)} ${unit}</title></rect><text x="${280+len}" y="${y+22}">${fmt(v[key],2)}</text>`;});el('metric-plot').innerHTML=svg;el('metric-caption').textContent=isForecast?'Diese Mengen sind Prognosen, keine Fehler. Eine höhere Zahl ist nicht automatisch besser. Alle Werte mit ERP-Korrektur und ohne Zusatzauftrag.':`${el('metric-mode').selectedOptions[0].textContent}: Kleinere Werte sind besser. Bereinigte Daten, dieselben zwei Testjahre für alle Verfahren.`;
}
if(el('annual-plot')){el('annual-mode').addEventListener('change',annual);el('season-mode').addEventListener('change',season);annual();season();}
if(el('metric-plot')){el('metric-mode').addEventListener('change',metric);metric();}
}catch(error){for(const id of ['annual-caption','metric-caption'])if(el(id))el(id).textContent='Die Diagrammdaten konnten nicht geladen werden. Die Tabellen und der Rechenweg bleiben verfügbar.';console.error(error);}
})();
