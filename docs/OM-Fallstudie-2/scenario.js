(()=>{
const $=id=>document.getElementById(id), f=n=>n.toLocaleString('de-DE',{minimumFractionDigits:2,maximumFractionDigits:2});
function update(){const p=+$('p').value/100,t=+$('t').value,c=+$('c').value,r=+$('release').value;
if(['p','t','c','release'].some(id=>!$(id).checkValidity()||$(id).value==='')){$('result').textContent='Bitte gültige Werte innerhalb der angezeigten Grenzen eingeben.';$('bars').replaceChildren();$('queue').textContent='';return;}
const caps=[900/31,30,450*(1-p)/t,900/31,450*c*(1-p)/37], names=['Antrieb','Box und Lenkung','Elektrik','Räder und Bremsen','Endkontrolle'],min=Math.min(...caps),out=Math.min(r,min),rho=out*37/((1-p)*450*c);
$('result').textContent=`Linienkapazität ${f(min)} · Durchsatz ${f(out)} Räder/Tag · Engpass: ${names.filter((_,i)=>Math.abs(caps[i]-min)<1e-8).join(' und ')}. ${r>min?'Tagesfreigabe überschreitet Kapazität.':'Tagesfreigabe ist kapazitiv erreichbar.'}`;
$('bars').replaceChildren();caps.forEach((v,i)=>{let row=document.createElement('div');row.className='capacity-row';let label=document.createElement('span');label.textContent=names[i]+' · '+f(v);let bar=document.createElement('div');bar.className='capacity-bar';bar.style.width=(100*v/Math.max(...caps))+'%';bar.style.background=Math.abs(v-min)<1e-8?'#a52c40':'#477b89';row.append(label,bar);$('bars').append(row);});
const baseline=Math.abs(p-.03)<1e-9&&t===15&&c===3&&r===26;
$('queue').textContent=`Prüfung: ${f(out/(1-p))} Besuche/Tag · Auslastung ${f(rho*100)} %. `+(baseline?'Referenzsimulation: Wq ≈ 19,5 min/Besuch unter Poisson-Annahme; siehe Wartezeitseite.':'Für dieses Szenario wurde keine Wartezeit simuliert. Auslastung allein bestimmt keine exakte Wartezeit.');
}
['p','t','c','release'].forEach(id=>$(id).addEventListener('input',update));
function preset(p,t,c){$('p').value=p;$('t').value=t;$('c').value=c;$('release').value=26;update();}
$('today').onclick=()=>preset(22,14,3);$('adapter').onclick=()=>preset(3,15,3);$('four').onclick=()=>preset(22,14,4);update();
})();
