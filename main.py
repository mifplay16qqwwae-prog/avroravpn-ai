import os, json, random, subprocess, math, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests

W,H,FPS,DURATION=720,1280,24,30
OUT=Path("output"); OUT.mkdir(exist_ok=True)

def ask_gemini():
    key=os.getenv("GEMINI_API_KEY")
    if not key: raise RuntimeError("Добавь GEMINI_API_KEY в GitHub Secrets")
    prompt="""Создай короткую смешную оригинальную историю для 2D мультфильма на русском, 30 секунд,
вертикальный формат. Главные герои: постоянный синий круглый персонаж Бублик с большими глазами
и маленький оранжевый робот Пиксель. Никаких чужих известных персонажей.
Сделай 5 сцен. Верни ТОЛЬКО JSON:
{"title":"...", "scenes":[{"background":"city|room|park|space","action":"короткое описание действия","dialogue":"короткая реплика"}],
"ending":"короткая финальная фраза с естественным упоминанием AvroraVPN"}
Сцены должны быть визуально простыми, смешными и понятными без знания контекста."""
    url="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="+key
    r=requests.post(url,json={"contents":[{"parts":[{"text":prompt}]}],
        "generationConfig":{"responseMimeType":"application/json"}},timeout=60)
    r.raise_for_status()
    data=json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
    if len(data.get("scenes",[]))<3: raise RuntimeError("ИИ вернул слишком мало сцен")
    return data

def font(size,bold=False):
    candidates=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in candidates:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, maxw):
    words=text.split(); lines=[]; line=""
    for word in words:
        test=(line+" "+word).strip()
        if draw.textbbox((0,0),test,font=fnt)[2] <= maxw: line=test
        else:
            if line: lines.append(line)
            line=word
    if line: lines.append(line)
    return lines

def draw_scene(scene, idx, frame, total, title):
    t=frame/FPS
    palettes={"city":("#9bd8ff","#f5c66a"),"room":("#ffd6e7","#b4e4ff"),
              "park":("#a9e8b0","#77c9ed"),"space":("#24234f","#7963b5")}
    bg,ground=palettes.get(scene.get("background","city"),palettes["city"])
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    d.rectangle((0,900,W,H),fill=ground)
    # simple moving clouds / stars
    for j in range(5):
        x=(j*180+int(t*35))%(W+160)-80
        d.ellipse((x,140+j*45,x+110,190+j*45),fill="#ffffff")
    # character bounce and blink-like eyes
    bounce=int(math.sin(t*5+idx)*18)
    # Bublik
    cx,cy=245,760+bounce
    d.ellipse((cx-125,cy-125,cx+125,cy+125),fill="#2878ed",outline="#153b85",width=8)
    d.ellipse((cx-58,cy-40,cx-20,cy+8),fill="white"); d.ellipse((cx+20,cy-40,cx+58,cy+8),fill="white")
    d.ellipse((cx-43,cy-24,cx-27,cy-5),fill="#17233d"); d.ellipse((cx+35,cy-24,cx+51,cy-5),fill="#17233d")
    d.arc((cx-48,cy+5,cx+48,cy+75),0,180,fill="#102d63",width=8)
    # Pixel robot
    rx,ry=510,770-bounce
    d.rounded_rectangle((rx-85,ry-105,rx+85,ry+95),radius=28,fill="#ff963d",outline="#9b4b20",width=8)
    d.rectangle((rx-12,ry-155,rx+12,ry-105),fill="#9b4b20")
    d.ellipse((rx-24,ry-177,rx+24,ry-129),fill="#ffdf63")
    d.ellipse((rx-48,ry-48,rx-15,ry-10),fill="white"); d.ellipse((rx+15,ry-48,rx+48,ry-10),fill="white")
    d.ellipse((rx-34,ry-38,rx-21,ry-20),fill="#17233d"); d.ellipse((rx+28,ry-38,rx+41,ry-20),fill="#17233d")
    d.line((rx-28,ry+35,rx+28,ry+35),fill="#713514",width=7)
    # caption panel
    d.rounded_rectangle((35,75,W-35,270),radius=34,fill="#ffffff",outline="#26345c",width=5)
    caption=scene.get("dialogue","")
    lines=wrap(d,caption,font(34,True),W-110)
    yy=115
    for line in lines[:3]:
        d.text((60,yy),line,font=font(34,True),fill="#18213b"); yy+=48
    # title / branding
    d.rounded_rectangle((35,1130,W-35,1225),radius=25,fill="#111b35")
    d.text((65,1150),"AvroraVPN",font=font(43,True),fill="white")
    d.text((390,1165),f"Мульт-сериал • {idx+1}/5",font=font(23),fill="#b8d5ff")
    return im

def main():
    story=ask_gemini()
    (OUT/"story.json").write_text(json.dumps(story,ensure_ascii=False,indent=2),encoding="utf-8")
    scenes=story["scenes"][:5]
    per=max(1,(DURATION*FPS)//len(scenes))
    frames=OUT/"frames"; frames.mkdir(exist_ok=True)
    for i in range(DURATION*FPS):
        si=min(len(scenes)-1,i//per)
        img=draw_scene(scenes[si],si,i%per,per,story["title"])
        img.save(frames/f"{i:05d}.png")
    subprocess.run(["ffmpeg","-y","-framerate",str(FPS),"-i",str(frames/"%05d.png"),
        "-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS),str(OUT/"avroravpn_cartoon.mp4")],check=True)
    print("Готово: output/avroravpn_cartoon.mp4")
    print("Это прототип 2D-анимации с движущимися персонажами и репликами; полноценная генерация рисованных сцен и публикация TikTok подключаются отдельно.")

if __name__=="__main__": main()
