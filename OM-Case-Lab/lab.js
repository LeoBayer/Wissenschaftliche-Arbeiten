(async function(){
  'use strict';
  const root=document.getElementById('decision-lab');if(!root)return;
  const num=(v,d=1)=>new Intl.NumberFormat('de-DE',{maximumFractionDigits:d,minimumFractionDigits:d}).format(v);
  const eur=v=>new Intl.NumberFormat('de-DE',{style:'currency',currency:'EUR',maximumFractionDigits:0}).format(v);
  let baseline;
  try{const response=await fetch('data.json');if(!response.ok)throw Error('Daten nicht verfügbar');baseline=await response.json();}
  catch(e){root.textContent='Die Falldaten konnten nicht geladen werden. Bitte über einen lokalen Webserver oder die Website öffnen.';return;}
  root.innerHTML=`<form id="lab-form" novalidate><div class="lab-controls">
    <label for="method">Prognosemodell<select id="method"><option value="constant">Konstant: letzter Jahresabsatz</option><option value="linear">Linearer Trend</option><option value="exponential">Exponentieller Trend (Log-OLS)</option></select></label>
    <label for="factor">Nachfragefaktor<input id="factor" type="number" min="0" max="5" step="0.05"><small>1 = Modellprognose; 0,7 = 30 % weniger. Szenario, keine Wahrscheinlichkeit.</small></label>
    <label for="price">Nettoverkaufspreis · €/Stück<input id="price" type="number" min="0" max="100000" step="0.01"></label>
    <label for="cost">Variable Kosten · €/Stück<input id="cost" type="number" min="0" max="100000" step="0.01"></label>
    <label for="fixed">Fixkosten · €/Jahr<input id="fixed" type="number" min="0" max="10000000" step="1"></label>
    <label for="avoidable">Bei Einstellung vermeidbar · %<input id="avoidable" type="number" min="0" max="100" step="1"><small>100 % ist die korrigierte Persona-Auskunft. Kleinere Werte testen die Kostenrelevanz.</small></label>
    <label for="rate">Kalkulationszins · %/Jahr<input id="rate" type="number" min="0" max="100" step="0.1"><small>Voreinstellung 0 %: undiskontierte Rechnung; kein Zinssatz vorgegeben.</small></label>
    <label for="setup">Zusätzliche Einmalkosten · €<input id="setup" type="number" min="0" max="10000000" step="1"><small>Voreinstellung 0: bislang nicht belegt. Aufwand zum Entscheidungszeitpunkt.</small></label>
  </div><details class="answer"><summary>Historische Daten für ein eigenes Experiment ändern</summary><p>Nur im Browser. Die belegten Ausgangsdaten werden nicht überschrieben.</p><div class="lab-controls">${baseline.years.map((y,i)=>`<label for="history-${i}">GJ ${y} · Stück<input id="history-${i}" type="number" min="1" max="1000000" step="1"></label>`).join('')}</div></details>
  <div class="lab-actions"><button type="button" id="reset-lab">Ausgangsfall wiederherstellen</button><button type="button" id="export-json">Szenario als JSON</button><button type="button" id="export-csv">Rechenweg als CSV</button></div></form>
  <p id="scenario-label"></p><div id="lab-result" aria-live="polite" aria-atomic="true"></div>`;
  const ids=['method','factor','price','cost','fixed','avoidable','rate','setup'];
  let latest=null;
  document.getElementById('lab-form').addEventListener('submit',e=>e.preventDefault());
  function reset(){ids.forEach(k=>document.getElementById(k).value=(k==='avoidable'||k==='rate')?baseline[k]*100:baseline[k]);baseline.history.forEach((v,i)=>document.getElementById('history-'+i).value=v);update();}
  function read(){
    const state={};
    for(const id of ids){const el=document.getElementById(id);if(!el.checkValidity()||el.value==='')throw Error('Bitte alle Felder innerhalb der angegebenen Grenzen ausfüllen.');state[id]=id==='method'?el.value:Number(el.value);}
    state.avoidable/=100;state.rate/=100;
    state.history=baseline.history.map((_,i)=>{const el=document.getElementById('history-'+i);if(!el.checkValidity()||!el.value)throw Error('Historische Absätze müssen positive ganze Stückzahlen sein.');return Number(el.value);});
    return state;
  }
  const table=(heads,rows)=>`<div class="table-wrap"><table><thead><tr>${heads.map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map((x,i)=>i?`<td>${x}</td>`:`<th scope="row">${x}</th>`).join('')}</tr>`).join('')}</tbody></table></div>`;
  function chart(history,q){
    const all=history.concat(q),max=Math.max(50,...all)*1.15,W=760,H=300,L=55,R=15,T=30,B=45;
    const x=i=>L+i*(W-L-R)/6,y=v=>H-B-v*(H-T-B)/max;
    const line=(vals,start,color,dash='')=>`<polyline fill="none" stroke="${color}" stroke-width="3" ${dash?'stroke-dasharray="6 5"':''} points="${vals.map((v,i)=>`${x(i+start)},${y(v)}`).join(' ')}"/>`;
    return `<svg role="img" aria-labelledby="forecast-title forecast-description" viewBox="0 0 ${W} ${H}"><title id="forecast-title">Erfasste Mengen und Drei-Jahres-Szenario</title><desc id="forecast-description">Erfasste historische Mengen blau, Szenarioprognose gestrichelt in Rosa. Alle Zahlen stehen auch in den Tabellen. Stück pro Geschäftsjahr.</desc>${[0,1,2,3,4].map(i=>{const v=i*max/4;return `<line x1="${L}" y1="${y(v)}" x2="${W-R}" y2="${y(v)}" stroke="currentColor" opacity=".15"/><text x="${L-8}" y="${y(v)+4}" fill="currentColor" text-anchor="end" font-size="12">${num(v,0)}</text>`}).join('')}<text x="${L}" y="16" fill="currentColor" font-size="12">Stück / Geschäftsjahr</text>${all.map((v,i)=>`<text x="${x(i)}" y="${H-18}" text-anchor="middle" fill="currentColor" font-size="13">${2023+i}</text>`).join('')}${line(history,0,'#16828a')}${line([history[3],...q],3,'#bd4776',true)}${all.map((v,i)=>`<circle cx="${x(i)}" cy="${y(v)}" r="4" fill="${i<4?'#16828a':'#bd4776'}"/>`).join('')}</svg><p class="chart-legend">● Beobachtung · – – Szenario (Erwartungswerte, keine zugesagte Nachfrage)</p>`;
  }
  function update(){
    const result=document.getElementById('lab-result');latest=null;
    try{
      const s=read(),q=OMModel.forecast(s.history,s.method).map(v=>v*s.factor),e=OMModel.economics(q,s.price,s.cost,s.fixed,s.avoidable,s.rate,s.setup);
      if(!Number.isFinite(e.npv))throw Error('Ergebnis außerhalb des gültigen Zahlenbereichs.');
      const changed=ids.some(k=>s[k]!==baseline[k])||s.history.some((v,i)=>v!==baseline.history[i]);
      document.getElementById('scenario-label').textContent=changed?'EXPERIMENT · gegenüber dem Ausgangsfall verändert. Kein neuer Beleg.':'AUSGANGSFALL · linearer Referenztrend; unbestätigte Vertragsdetails bleiben offen.';
      const comparisons=['constant','linear','exponential'].map(m=>{const qq=OMModel.forecast(s.history,m).map(v=>v*s.factor),ee=OMModel.economics(qq,s.price,s.cost,s.fixed,s.avoidable,s.rate,s.setup),bt=OMModel.backtest(s.history,m);return {method:m,q:qq,economics:ee,backtest:bt};});
      const labels={constant:'Konstant (naiv)',linear:'Linear',exponential:'Exponentiell'};
      const stress=[.7,1,1.3].map(f=>{const qq=OMModel.forecast(s.history,s.method).map(v=>v*s.factor*f),ee=OMModel.economics(qq,s.price,s.cost,s.fixed,s.avoidable,s.rate,s.setup);return [num(s.factor*f,2),eur(ee.npv),ee.npv>=0?'Fortführung vorteilhaft':'Nichtverlängerung vorteilhaft'];});
      result.innerHTML=`<div class="stats"><div class="stat">Vorteil gegenüber Einstellung<strong>${eur(e.npv)}</strong><small>${s.rate?'Barwert':'Summe'} 2027–2029, nach Einmalkosten</small></div><div class="stat">Deckungsbeitrag pro Akku<strong>${eur(e.margin)}</strong><small>Preis minus variable Stückkosten</small></div><div class="stat">Erforderliche konstante Jahresmenge<strong>${e.threshold===null?'Kein positiver DB':num(e.threshold,1)+' Stück'}</strong><small>Entscheidungsschwelle bei diesen Kosten und diesem Zins</small></div></div>
      <p class="status">${e.npv>0?'Unter diesen Annahmen spricht die Rechnung für die Fortführung.':e.npv<0?'Unter diesen Annahmen spricht die Rechnung gegen die Fortführung.':'Unter diesen Annahmen sind beide Optionen finanziell gleichwertig.'} Das ist eine bedingte Empfehlung, keine Nachfragesicherheit.</p>
      <div class="chart">${chart(s.history,q)}</div>
      <h3>Vom Absatz zur Entscheidung</h3>${table(['GJ','Prognose · Stück','DB · €','Fortführen · €','Einstellen · €','Differenz · €'],e.rows.map(r=>[r.year,num(r.quantity,2),eur(r.contribution),eur(r.continuation),eur(r.stop),eur(r.delta)]))}
      <p>Berechnet mit ungerundeten Werten. Die Anzeige rundet; Prognosen sind Erwartungswerte. Einmalaufwand von ${eur(s.setup)} wird zusätzlich abgezogen. ${s.rate?'Die Jahresdifferenzen werden auf den Entscheidungszeitpunkt abgezinst.':'Keine Abzinsung im gewählten Szenario.'}</p>
      <h3>Wie viel Abweichung hält die Entscheidung aus?</h3><p>${e.demandFactor===null?'Für eine Nullmengenprognose oder einen nichtpositiven Deckungsbeitrag ist diese Schwelle nicht ableitbar.':`Die gewählte Absatzkurve müsste mindestens <strong>${num(e.demandFactor*100,1)} %</strong> ihrer aktuell angezeigten Mengen erreichen. Bei unveränderten Mengen läge der kostendeckende Verkaufspreis bei <strong>${eur(e.breakEvenPrice)}</strong>.`} Diese Werte sind rechnerische Schwellen, keine Konfidenzintervalle.</p>
      ${table(['Nachfragefaktor insgesamt','Vorteil · 3 Jahre','Rechnerische Richtung'],stress)}
      <h3>Modellvergleich statt Lieblingskurve</h3>${table(['Modell','2027','2028','2029','Vorteil · €','Test-MAE · Stück','Test-MSE · Stück²'],comparisons.map(c=>[labels[c.method],...c.q.map(v=>num(v,1)),eur(c.economics.npv),num(c.backtest.mad,2),num(c.backtest.mse,2)]))}
      <p>Test: zwei echte Ein-Schritt-Prognosen für 2025 und 2026, jeweils nur aus den zuvor bekannten Daten. Die Testfehler beziehen sich auf die unveränderte Modellprognose vor Nachfragefaktor. Nur zwei Testpunkte: kein belastbarer Nachweis für drei weitere Jahre. Der lineare Trend ist ein vorsichtigerer Referenzfall gegenüber exponentieller Fortschreibung, nicht nachgewiesen überlegen.</p>`;
      latest={version:baseline.version,created:new Date().toISOString(),inputs:s,forecast:q,economics:e,comparisons};
    }catch(err){document.getElementById('scenario-label').textContent='EINGABE PRÜFEN';result.innerHTML='';const p=document.createElement('p');p.className='status error';p.textContent=err.message;result.append(p);}
    document.getElementById('export-json').disabled=!latest;document.getElementById('export-csv').disabled=!latest;
  }
  function save(name,text,type){const u=URL.createObjectURL(new Blob([text],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
  document.getElementById('reset-lab').addEventListener('click',reset);
  document.getElementById('lab-form').addEventListener('input',update);document.getElementById('method').addEventListener('change',update);
  document.getElementById('export-json').addEventListener('click',()=>{if(latest)save('om-ersatzakku-szenario.json',JSON.stringify(latest,null,2),'application/json');});
  document.getElementById('export-csv').addEventListener('click',()=>{if(!latest)return;const rows=[['GJ','Menge','Deckungsbeitrag_EUR','Fortfuehren_EUR','Einstellen_EUR','Differenz_EUR','Barwert_Differenz_EUR'],...latest.economics.rows.map(r=>[r.year,r.quantity,r.contribution,r.continuation,r.stop,r.delta,r.pv]),['Einmalkosten_EUR',latest.inputs.setup],['Vorteil_Barwert_EUR',latest.economics.npv]];save('om-ersatzakku-rechenweg.csv','\ufeff'+rows.map(r=>r.map(v=>typeof v==='number'?String(v).replace('.',','):v).join(';')).join('\r\n'),'text/csv;charset=utf-8');});
  reset();
})();
