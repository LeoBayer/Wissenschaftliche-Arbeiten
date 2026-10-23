"""Finite local browser/math/export verification and print-to-PDF build."""
import json, threading, shutil
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright

SOURCE=Path(__file__).resolve().parent
SITE=SOURCE/'_site'
REPORT=Path('/home/leo/.local/state/openclaw/om-lernwerkstatt-2026-10-23/site-review')
REPORT.mkdir(exist_ok=True)
CHROME='/home/leo/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'

class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(SITE)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_port}'
results={'math':{},'viewports':[],'pages':[]}
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROME,headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
        context.route('**/*',lambda route:route.continue_() if route.request.url.startswith(base) else route.abort())
        page=context.new_page();page.set_default_timeout(8000)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base+'/labor.html');page.locator('#lab-result .stats').wait_for()
        math=page.evaluate('''()=>{
          const M=OMModel,q=M.forecast([10,15,25,38],'linear');
          const e=M.economics(q,690,440,10000,1);
          const naive=M.economics([38,38,38],690,440,10000,1);
          const unavoidable=M.economics([38,38,38],690,440,10000,0);
          const stress=M.economics(q.map(v=>v*.7),690,440,10000,1);
          const flat=M.forecast([10,10,10,10],'linear');
          const zero=M.economics([0,0,0],690,440,10000,1);
          const margin=M.economics([40,40,40],440,440,10000,1);
          const bt=M.backtest([10,15,25,38],'constant');
          const discounted=M.economics([40,40,40],690,440,10000,1,.1,1000);
          return {q,npv:e.npv,threshold:e.threshold,factor:e.demandFactor,naive:naive.npv,
           unavoidable:unavoidable.npv,stress:stress.npv,flat,zero:zero.npv,
           zeroMarginThreshold:margin.threshold,backtest:bt,discounted:discounted.npv};
        }''')
        assert all(abs(a-b)<1e-8 for a,b in zip(math['q'],[45.5,54.9,64.3]))
        for key,expected in [('npv',11175),('threshold',40),('naive',-1500),('unavoidable',28500),('stress',-1177.5),('zero',-30000),('discounted',-1000)]:
            assert abs(math[key]-expected)<1e-7,(key,math[key])
        assert math['flat']==[10,10,10] and math['zeroMarginThreshold'] is None
        assert math['backtest']['n']==2 and abs(math['backtest']['mse']-134.5)<1e-8
        results['math']=math
        page.locator('#factor').fill('0.7');assert 'EXPERIMENT' in page.locator('#scenario-label').inner_text()
        assert 'Nichtverlängerung vorteilhaft' in page.locator('#lab-result').inner_text()
        assert '1.178' in page.locator('#lab-result').inner_text(), 'Negative half-euro amount must round consistently after cent normalization.'
        page.locator('#price').fill('');assert page.locator('#lab-result .error').count()==1
        assert page.locator('#export-json').is_disabled()
        page.locator('#reset-lab').click();assert 'AUSGANGSFALL' in page.locator('#scenario-label').inner_text()
        page.locator('#method').select_option('exponential');assert 'EXPERIMENT' in page.locator('#scenario-label').inner_text()
        page.locator('#reset-lab').click()
        for kind in ('json','csv'):
            with page.expect_download() as info:page.locator('#export-'+kind).click()
            download=info.value;download.save_as(REPORT/download.suggested_filename)
        scenario=json.loads((REPORT/'om-ersatzakku-szenario.json').read_text())
        assert abs(scenario['economics']['npv']-11175)<1e-8
        for width in (1440,1024,768,390,320):
            page.set_viewport_size({'width':width,'height':1000})
            dims=page.evaluate('({viewport:innerWidth,body:document.documentElement.scrollWidth})')
            assert dims['body']<=width+1,(width,dims)
            page.screenshot(path=str(REPORT/f'labor-light-{width}.png'),full_page=True)
            results['viewports'].append(dims)
        page.set_viewport_size({'width':1440,'height':1000})
        page.goto(base+'/labor.html');page.locator('#lab-result .stats').wait_for()
        toggle=page.locator('a.quarto-color-scheme-toggle').first
        if toggle.count():toggle.click()
        assert 'quarto-dark' in page.locator('body').get_attribute('class')
        page.screenshot(path=str(REPORT/'labor-dark-1440.png'),full_page=True)
        toggle.click()
        # Render PDF without screen navigation. Link remains a clickable PDF annotation.
        page.goto(base+'/abgabe.html');page.locator('main h1').wait_for()
        page.emulate_media(media='print')
        page.add_style_tag(content='''@page {size:A4; margin:15mm 15mm 18mm;} h2,h3 {break-after:avoid;} tr {break-inside:avoid;} .quarto-title-block {margin-bottom:1rem;} .quarto-container {margin:0!important;padding:0!important;} #quarto-content {padding:0!important;}''')
        (SOURCE/'downloads').mkdir(exist_ok=True);(SITE/'downloads').mkdir(exist_ok=True)
        pdf=SOURCE/'downloads/ersatzakku-probeabgabe.pdf'
        page.pdf(path=str(pdf),format='A4',print_background=True,prefer_css_page_size=True,
                 display_header_footer=True,header_template='<span></span>',
                 footer_template='<div style="width:100%;font-size:8px;text-align:center;color:#666">OM · unbewertete Probeanalyse · 23.10.2026 · <span class="pageNumber"></span>/<span class="totalPages"></span></div>')
        shutil.copy2(pdf,SITE/'downloads'/pdf.name)
        page.emulate_media(media='screen')
        for name in ('index','labor','methode','verstehen','abgabe'):
            page.goto(base+'/'+name+'.html');page.locator('main h1').wait_for()
            results['pages'].append({'name':name,'title':page.title()})
            if name=='verstehen':
                page.locator('details summary').first.click();assert page.locator('details').first.get_attribute('open') is not None
        # All local anchors/resources exposed through HTML resolve.
        from html.parser import HTMLParser
        from urllib.parse import urlparse,unquote
        class Links(HTMLParser):
            def handle_starttag(self,tag,attrs):
                for key,value in attrs:
                    if key not in ('href','src') or not value:continue
                    u=urlparse(value)
                    if u.scheme or u.netloc or not u.path:continue
                    target=SITE/unquote(u.path.lstrip('/'))
                    assert target.exists(),(tag,value)
        for html in SITE.glob('*.html'):Links().feed(html.read_text())
        assert not errors,errors
        results['javascript_errors']=errors
        results['exports_verified']=True
        browser.close()
finally:
    server.shutdown();server.server_close();thread.join()
(REPORT/'checks.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
