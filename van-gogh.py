#!/usr/bin/python
import os
import subprocess
import sys
sys.path.append('./modules')
import simplejson as json
import hasher
import magic
import web

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
    pass

_url = 'http://localhost/'

def url(img): 
    if not img: return str(img)
    return _url+img

def thumb(filepath):
    cmd = 'convert -geometry 151 %s t_%s' % (filepath, filepath)
    os.popen(cmd)
    
def validate(randname):

    newname = ''
    filetype = { 'JPEG' : 'jpg', 
                 'GIF ' : 'gif', 
                 'PNG ': 'png', 
                 'JPG ':'jpg' }

    fileext = magic.from_buffer(open(randname).read(1024))[:4]

    if fileext in filetype:
        fileext = filetype[fileext]
        newname = str(randname) + '.' + str(fileext)

        hashed = hasher.append(hasher.hasher(randname, newname))

        if hashed: 
            os.remove(randname)
            return hashed

        cmd = 'mv %s %s' % (randname, newname)
        os.popen(cmd)
        thumb(newname)
        return newname

    else: 
        os.remove(randname)
        return None

    

def upload(data, remote=False):

    randname = name()

    if remote:
        cmd = '''curl -L '%s' -o %s''' % (data, randname)
        if subprocess.call(cmd, shell=True):
            return None

    else:   
        open(randname, 'w').write(data)

    result = validate(randname)

    return result

def process(form, api=False):
    urls = []

    if api:
        for data in form:
            if data:
                urls.append(upload(data, True))
        return urls

    if form.localdata:
        for data in form.localdata:
            if data:
                urls.append(upload(data))

    if form.remotedata:
        for data in form.remotedata[0].splitlines():
            if data:
                urls.append(upload(data, True))



    return urls


def name():
    randname = os.popen('python modules/name.py').read()
    while os.path.exists(randname):randname=os.popen('python name.py').read()
    return randname 
            
class index:
    def __init__(self):
        self.html = '''<!DOCTYPE html>
	    <html lang='en'><head>
        <link href='/static/greetings.css' rel='stylesheet' type='text/css' /> 
	    <title>vincent</title></head>
        <meta http-equiv='content-type' content='text/html; charset=UTF-8' />
	    <body><div id='container'><div class='contain'><div class='up'>
	    <form action='' method='post' enctype='multipart/form-data' name='vangogh'>
	    <input name='localdata' type=file multiple class='hello' value='' />
	    <input type='submit' class='submitbuttn1' /></div><div>
	    <textarea name='remotedata' type='textarea' class='goodbye'
        placeholder='separate urls with a new line'></textarea> 
	    </form></div>'''

    def GET(self):
        return self.html

    def POST(self):
        user_data = web.input(localdata=[None], remotedata=[None], api=[None])
        posthtml = '<div id=urlinput>\n'
        posthtml2 = "<div id=urltextarea>\n<textarea>"
        for filepath in process(user_data):
            if filepath:
                posthtml += '''<div><input type='text' value='%s'class='url' /><br />
                        <img src='%s' alt='%s' class='uploaded' /></div>
                        ''' % (url(filepath), url('t_'+filepath), url('t_'+filepath))
                posthtml2 += url(filepath)+'\n'
        posthtml += '</div>'
        posthtml2 += '</textarea></div>'
        return self.html+posthtml2+posthtml

class api: 
    def __init__(self):
        self.count = 0
        self.response = {}
        self.user_data = web.input(url=[None])

    def GET(self): 
        for img in process(self.user_data.url, True):
            self.response['image'+str(self.count)] = url(img)
            self.count += 1
        return json.dumps(self.response)

    def POST(self):
        for img in process(self.user_data.url, True):
            self.response['image'+str(self.count)] = url(img)
            self.count += 1
        return self.response
      
class images:
    def GET(self,name):
        ext = name.split(".")[-1] # Gather extension

        cType = {
            "png":"image/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"            }

        if name in os.listdir('.'):  # Security
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('%s'%name,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()

urls = ( '/', 'index', '/(.*)', 'images', '/api', 'api', '/images/(.*)', 'images' )
  
if __name__ == '__main__':
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()  
