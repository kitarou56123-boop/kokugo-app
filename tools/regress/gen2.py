exec(open('gen.py').read().split("WORDS=")[0])
import json
cases=[]
OUT='/home/claude/kokugo-app/_reg2'; os.makedirs(OUT,exist_ok=True)
CH="吚呻噢楳槑呣嗚咽囁囈噫嘔嚔嚏嚬嚶囃囀嚼嚥噛噎嘸嘯嘶嘲嘴嘛嘘嗽嗾嗅嗄嗇喩喙喘喀啖啜啄唾唸唳唹哽哮哭咤咢咬咫咥咸咨咳哀呟呷呵咀呱"
def add(im,ans,tag):
    n=f'r{len(cases):04d}'; im.save(f'{OUT}/{n}.png'); cases.append(dict(f=n+'.png',ans=ans,mode='sel',tag=tag))
for c in CH:
    for fn,f in FON:
        for k in ['きれい','写真風','ぼけ']: add(degrade(hor([c],f),k),c,'珍1字・'+k)
json.dump(cases,open(f'{OUT}/cases.json','w'),ensure_ascii=False); print(len(cases))
