from handlers.base import BaseHandler
from settings import settings
from random import randint as rint
import StringIO
import Image, ImageDraw, ImageFont
class ValidCodeCaptchaHandler(BaseHandler):
    def get(self):
        # Create a background image
        Path = settings['static_path']
        image = Image.new('RGB', (80, 30), (200,0,0))
        draw = ImageDraw.Draw(image)
        n1,n2,n3,n4 = rint(1,9), rint(1,9), rint(1,9), rint(1,9)
        validcode = '{0}{1}{2}{3}'.format(n1,n2,n3,n4)
        self.session['validcode'] = validcode

        # Create a text image
        textImg = Image.new('RGB',(80,25),(0,0,0))

        tmpDraw = ImageDraw.Draw(textImg)
        textFont = ImageFont.truetype(Path+'/arial.ttf',24)
        tmpDraw.text((0, 0), validcode, font = textFont, fill = (255,255,255))
        textImg = textImg.rotate(5)

        # Create a mask (same size as the text image)
        mask = Image.new('L',(80, 25),0)
        mask.paste(textImg,(0,0))
         
        # Paste text image with the mask
        image.paste(textImg,(10,0),mask)
        f = StringIO.StringIO()
        image.save(f, "PNG")
        self.set_header("Content-Type", "image/png")    
        contents = f.getvalue()  
        self.write(contents)
        f.close()


class RegisterCaptchaHandler(BaseHandler):
    def get(self):
        # Create a background image
        Path = settings['static_path']
        image = Image.new('RGB', (80, 30), (100,200,0))
        draw = ImageDraw.Draw(image)
        n1,n2,n3,n4 = rint(1,9), rint(1,9), rint(1,9), rint(1,9)
        validcode = '{0}{1}{2}{3}'.format(n1,n2,n3,n4)
        self.session['registercode'] = validcode
        # Create a text image
        textImg = Image.new('RGB',(80,25),(0,0,0))
        tmpDraw = ImageDraw.Draw(textImg)
        textFont = ImageFont.truetype(Path+'/arial.ttf',24)
        tmpDraw.text((0, 0), validcode, font = textFont, fill = (255,255,255))
        textImg = textImg.rotate(5)        
        # Create a mask (same size as the text image)
        mask = Image.new('L',(80, 25),0)
        mask.paste(textImg,(0,0))
         
        # Paste text image with the mask
        image.paste(textImg,(10,0),mask)
        f = StringIO.StringIO()
        image.save(f, "PNG")
        self.set_header("Content-Type", "image/png")  
        contents = f.getvalue()  
        self.write(contents)
        f.close()