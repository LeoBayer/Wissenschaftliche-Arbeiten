/* Pure decision model. Fractional forecasts are expectations, not order quantities. */
(function (g) {
  'use strict';
  function fit(history, method) {
    if (!Array.isArray(history) || history.length < 2 || history.some(v => !Number.isFinite(v) || v < 0)) throw Error('Mindestens zwei nichtnegative Beobachtungen nötig.');
    if (method === 'constant') return () => history[history.length - 1];
    if (!['linear', 'exponential'].includes(method)) throw Error('Unbekanntes Modell.');
    if (method === 'exponential' && history.some(v => v <= 0)) throw Error('Exponentialmodell benötigt positive Werte.');
    const ys = method === 'exponential' ? history.map(Math.log) : history;
    const n = ys.length, xm = (n - 1) / 2, ym = ys.reduce((a,b)=>a+b,0)/n;
    let xy=0, xx=0;
    ys.forEach((y,i)=>{xy+=(i-xm)*(y-ym);xx+=(i-xm)**2;});
    const b=xy/xx, a=ym-b*xm;
    return x => Math.max(0,method==='exponential'?Math.exp(a+b*x):a+b*x);
  }
  function forecast(history,method,horizon=3) {const f=fit(history,method);return Array.from({length:horizon},(_,i)=>f(history.length+i));}
  function backtest(history,method) {
    const rows=[];
    for(let i=2;i<history.length;i++) {const pred=fit(history.slice(0,i),method)(i);rows.push({index:i,actual:history[i],pred,error:history[i]-pred});}
    return {rows,n:rows.length,mse:rows.reduce((s,r)=>s+r.error**2,0)/rows.length,mad:rows.reduce((s,r)=>s+Math.abs(r.error),0)/rows.length};
  }
  function economics(q,p,c,fixed,avoidable,rate=0,setup=0) {
    if(q.some(v=>!Number.isFinite(v)||v<0)||![p,c,fixed,avoidable,rate,setup].every(Number.isFinite)||p<0||c<0||fixed<0||avoidable<0||avoidable>1||rate<0||setup<0) throw Error('Ungültige Modellparameter.');
    const rows=q.map((quantity,i)=>{const contribution=quantity*(p-c), continuation=contribution-fixed,stop=avoidable===1?0:-fixed*(1-avoidable);return {year:2027+i,quantity,contribution,continuation,stop,delta:continuation-stop,pv:(continuation-stop)/(1+rate)**(i+1)};});
    const npv=rows.reduce((s,r)=>s+r.pv,0)-setup;
    const annuity=rows.reduce((s,r,i)=>s+1/(1+rate)**(i+1),0);
    const volumePV=rows.reduce((s,r,i)=>s+r.quantity/(1+rate)**(i+1),0);
    const requiredPV=fixed*avoidable*annuity+setup;
    const margin=p-c;
    return {rows,npv,margin,threshold:margin>0?requiredPV/(margin*annuity):null,demandFactor:margin>0&&volumePV>0?requiredPV/(margin*volumePV):null,breakEvenPrice:volumePV>0?c+requiredPV/volumePV:null};
  }
  g.OMModel={fit,forecast,backtest,economics};
})(globalThis);
