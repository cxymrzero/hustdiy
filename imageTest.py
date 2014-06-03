#coding:utf-8
import Image
import ImageDraw

im = Image.open('1.png')
draw = ImageDraw.Draw(im)
cn = "中文"
cn = cn.encode('unicode')
draw.text((100, 50), cn)
im.show()
im.save('2.png')
