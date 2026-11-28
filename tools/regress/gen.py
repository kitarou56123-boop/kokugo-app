import os,json,random,math,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
random.seed(7); np.random.seed(7)
OUT='/home/claude/kokugo-app/_reg'; os.makedirs(OUT,exist_ok=True)
def jp(p):
    for i in range(10):
        if 'JP' in ImageFont.truetype(p,20,index=i).getname()[0]: return i
FON=[('明朝','/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'),('ゴシック','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
FON=[(n,ImageFont.truetype(p,64,index=jp(p))) for n,p in FON]
def degrade(im,k):
    if k=='きれい': return im
    if k=='ぼけ': return im.filter(ImageFilter.GaussianBlur(2.2))
    if k=='傾き': return im.rotate(random.choice([-6,6]),expand=True,fillcolor='white')
    if k=='小さい':
        w,h=im.size; s=22/min(w,h); return im.resize((max(1,int(w*s)),max(1,int(h*s)))).resize((w,h))
    if k=='写真風':
        a=np.array(im).astype(np.float32); h,w=a.shape[:2]
        a=a*0.85*np.linspace(0.75,1,w)[None,:,None]+np.random.normal(0,14,a.shape)+20
        im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1))
        _,e=cv2.imencode('.jpg',np.array(im)[:,:,::-1],[cv2.IMWRITE_JPEG_QUALITY,35]); return Image.fromarray(cv2.imdecode(e,1)[:,:,::-1])
    if k=='白抜き':   # 暗い板に白い字（キーボードなど）
        a=255-np.array(im).astype(np.float32); a=a*0.75+40+np.random.normal(0,10,a.shape)
        return Image.fromarray(np.clip(a,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
KINDS=['きれい','ぼけ','傾き','小さい','写真風','白抜き']
def hor(lines,f):
    W=max(int(f.getlength(l)) for l in lines)+60; H=len(lines)*90+40
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    for i,l in enumerate(lines): d.text((30,20+i*90),l,font=f,fill='black')
    return im
def ver(cols,f):
    n=max(len(c) for c in cols); W=len(cols)*95+40; H=n*72+40
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    for j,c in enumerate(cols):
        x=W-25-(j+1)*95+12
        for i,ch in enumerate(c): d.text((x,20+i*72),ch,font=f,fill='black')
    return im
WORDS="兪 掖済会 圧迫骨折 鰆 鱚 鰯 鯵 鱸 嘉 齋藤 薔薇 憂鬱 檸檬 麒麟 葛飾 畝刈 長与町 蹲踞 剥離骨折 踵骨 脛骨 腓骨 大腿骨 褥瘡 嚥下 膝蓋骨 椎間板 痙攣 鼠径部 顎関節 蜂窩織炎 鷲 鶯 薙刀 饂飩 蕎麦 躑躅 蒟蒻 甑島 雫石 邊見 無変換 変更 鉄道 発売 鶏肉 衛生 義務 国会 大学 広島 桜島 富山 高校 吉野".split()
NAMES="髙橋 高橋 山﨑 山崎 濵田 浜田 濱田 冨士 富士 渡邉 渡辺 渡邊 齋藤 斎藤 𠮷田 吉田".split()
cases=[]
def add(im,ans,mode,tag):
    n=f'{len(cases):04d}'; im.save(f'{OUT}/{n}.png'); cases.append(dict(f=n+'.png',ans=ans,mode=mode,tag=tag))
for w in WORDS+NAMES:
    for fn,f in FON:
        for k in KINDS: add(degrade(hor([w],f),k),w,'sel','横・'+k+('・名前' if w in NAMES else ''))
        if len(w)>=2:
            for k in ['きれい','写真風','傾き']: add(degrade(ver([w],f),k),w,'sel','縦・'+k)
# 2行・2列
for a,b in [('圧迫骨折','大腿骨頸部'),('褥瘡予防','嚥下訓練'),('山高','水長'),('鶏肉','大豆')]:
    for fn,f in FON:
        add(hor([a,b],f),a+'\n'+b,'sel','横2行'); add(degrade(ver([a,b],f),'写真風'),a+'\n'+b,'sel','縦2列')
# 写真全体（囲まない）
PARA=[["本日の外来は午前九時から","受付は八時半に始まります","保険証を忘れずにお持ちください"],
      ["原材料名：鶏肉、玉ねぎ","しょうゆ（大豆・小麦を含む）","食塩、香辛料、調味料"],
      ["整形外科　第二診察室","膝関節・股関節の痛み","圧迫骨折のコルセット相談"],
      ["魚へんの字：鰆・鱚・鰯","鯛・鮪・鮭・鰻・鯖","鰹・鯉・鮎・鱸・鰈"]]
for p in PARA:
    for fn,f in FON:
        for k in ['きれい','写真風']: add(degrade(hor(p,f),k),'\n'.join(p),'photo','写真全体・横・'+k)
    add(degrade(ver(p,FON[0][1]),'きれい'),'\n'.join(p),'photo','写真全体・縦')
json.dump(cases,open(f'{OUT}/cases.json','w'),ensure_ascii=False)
from collections import Counter; print(len(cases), Counter(c['mode'] for c in cases))
