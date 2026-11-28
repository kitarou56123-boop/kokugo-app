import asyncio,json,os,sys,time
from playwright.async_api import async_playwright
ORT="/tmp/ortweb/node_modules/onnxruntime-web/dist/"; TJ="/tmp/ortweb/node_modules/tesseract.js/dist/"; TC="/tmp/ortweb/node_modules/tesseract.js-core/"
MODE=sys.argv[1] if len(sys.argv)>1 else 'now'; LIMIT=int(sys.argv[2]) if len(sys.argv)>2 else 99999
def ct(fn): return "application/wasm" if fn.endswith(".wasm") else ("application/gzip" if fn.endswith(".gz") else "text/javascript")
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
    ctx=await b.new_context(service_workers="block")
    async def cdn(route):
      u=route.request.url; fn=u.split('/')[-1].split('?')[0]
      if "@tesseract.js-data" in u:
        lp="/tmp/ortweb/node_modules/"+u.split("/npm/")[1]
        if os.path.exists(lp): return await route.fulfill(path=lp,headers={"Access-Control-Allow-Origin":"*"})
      for base in (ORT,TJ,TC):
        if os.path.exists(base+fn): return await route.fulfill(path=base+fn,headers={"Access-Control-Allow-Origin":"*","Content-Type":ct(fn)})
      print("MISS",u); await route.abort()
    await ctx.route("https://cdn.jsdelivr.net/**",cdn)
    async def tess(route):
      fn=route.request.url.split('/')[-1]
      if os.path.exists(fn): return await route.fulfill(path=fn,headers={"Access-Control-Allow-Origin":"*"})
      print("MISS",route.request.url); await route.abort()
    await ctx.route("https://tessdata.projectnaptha.com/**",tess)
    await ctx.route("https://huggingface.co/PaddlePaddle/**", lambda r: r.fulfill(path="/home/claude/ocrtest/"+("v5det.onnx" if "det_onnx" in r.request.url else "v5rec.onnx"), headers={"Access-Control-Allow-Origin":"*"}))
    await ctx.route("https://huggingface.co/LT8/**", lambda r: r.fulfill(path="/home/claude/ocrtest/lt8_"+r.request.url.split('/')[-1], headers={"Access-Control-Allow-Origin":"*"}))
    await ctx.route("https://fonts.googleapis.com/**", lambda r: r.abort())
    pg=await ctx.new_page(); pg.set_default_timeout(0); pg.on('console',lambda m: print(m.text[:150],flush=True) if m.text.startswith('CASE') or 'rror' in m.text else None)
    print("goto",flush=True); await pg.goto(os.environ.get("URL","http://localhost:8765/index.html"),wait_until="domcontentloaded",timeout=60000); print("loaded",flush=True); await pg.wait_for_timeout(3000); print("eval",flush=True)
    if MODE=='js':
      print(await pg.evaluate(open(os.environ['JS']).read()),flush=True); await b.close(); return
    if MODE=='dbg':
      await pg.evaluate("async()=>{ const im=new Image(); im.src='_reg/0000.png'; await im.decode(); const c=document.createElement('canvas'); c.width=im.width;c.height=im.height;c.getContext('2d').drawImage(im,0,0); window.__c=c; }")
      for step in ["ocrTry(ocrPrep(fitTextSize(cleanEdges(__c))),'jpn',6)","ocrTry(ocrPrep(fitTextSize(cleanEdges(__c))),'jpn_vert',5)","ocrTry(ocrPrep(fitTextSize(cleanEdges(__c))),'jpn',10)","getOcrWorker('jpn_vert').then(()=>'v')","loadV5()","loadYomi().then(()=>'y')","getOcrWorker('jpn').then(()=>'t')","loadHandModel().then(()=>'h')"]:
        try: print(step, await asyncio.wait_for(pg.evaluate("async()=>{ const t=performance.now(); await "+step+"; return Math.round(performance.now()-t); }"),60),flush=True)
        except Exception as e: print(step,'EXC',str(e)[:100],flush=True)
      await b.close(); return
    try: extra=open('/home/claude/regress/extra.js' if MODE!='det' else '/home/claude/regress/extra_det.js').read()
    except: extra=''
    res=await pg.evaluate("""async([MODE,LIMIT,EXTRA,FILT,REG])=>{
      try{camBusy=true;}catch(e){} window.__REG=REG; try{localStorage.setItem('gariben-prefetch','1');}catch(e){} if(EXTRA) (0,eval)(EXTRA);
      if(MODE==='notess'){ window.ocrTry=async()=>{ throw new Error('no tess'); }; }
      if(MODE==='det' && window.__setupDet) await window.__setupDet();
      let cases=(await (await fetch((window.__REG||'_reg')+'/cases.json')).json()); if(FILT) cases=cases.filter(c=>FILT.split(',').some(f=>c.tag.includes(f)||c.ans===f)); cases=cases.slice(0,LIMIT); const out=[];
      for(const c of cases){ if(MODE==='det' && c.mode!=='photo') continue; const im=new Image(); im.src=(window.__REG||'_reg')+'/'+c.f; await im.decode();
        const src=document.createElement('canvas'); src.width=im.width; src.height=im.height; src.getContext('2d').drawImage(im,0,0);
        console.log('CASE start '+c.f); const t0=performance.now(); let txt='';
        try{
          if(c.mode==='sel'){
            const cw=src.width,ch=src.height,m=Math.max(cw,ch),scale=m<1200?Math.min(4,1200/m):(m>1600?1600/m:1);
            const big=document.createElement('canvas'); big.width=Math.round(cw*scale); big.height=Math.round(ch*scale);
            const bg=big.getContext('2d'); bg.imageSmoothingQuality='high'; bg.drawImage(src,0,0,big.width,big.height);
            camSelR=ch/cw; const r=await ocrBest(fitTextSize(cleanEdges(big)),selPlan(ch/cw),()=>true,null); txt=r?r.text:'';
          } else {
            const s=Math.min(1.5,1800/Math.max(src.width,src.height)); let img=src;
            if(s>1.05){ img=document.createElement('canvas'); img.width=Math.round(src.width*s); img.height=Math.round(src.height*s); const g=img.getContext('2d'); g.imageSmoothingQuality='high'; g.drawImage(src,0,0,img.width,img.height); }
            camSelR=0;
            if(MODE==='det') txt=await window.__detRead(img); else { const r=await ocrBest(img,[["jpn",3,75],["jpn_vert",5]],()=>true,null); txt=r?r.text:''; }
          }
        }catch(e){ txt='ERR:'+e.message; }
        console.log('CASE '+c.f+' '+c.tag+' -> '+JSON.stringify(txt)+' '+Math.round(performance.now()-t0)); out.push({f:c.f,ans:c.ans,mode:c.mode,tag:c.tag,got:txt,ms:Math.round(performance.now()-t0)}); }
      return out; }""",[MODE,LIMIT,extra,os.environ.get("FILT",""),os.environ.get("REG","_reg")])
    json.dump(res,open(f'/home/claude/regress/res_{MODE}{os.environ.get("SUF","")}.json','w'),ensure_ascii=False)
    await b.close()
asyncio.run(main())
