import os
import base64
import py_compile
import tempfile

from django.conf.urls import url
from django.shortcuts import render


def bytecode(sourcefile):
    fd, tempname = tempfile.mkstemp()
    # Immediately close the file so that we can write/move it etc implicitly
    # below without nasty permission errors
    os.close(fd)
    try:
        py_compile.compile(sourcefile, cfile=tempname, doraise=True)
        with open(os.path.join(
                    os.path.dirname(sourcefile),
                    tempname
                ), 'rb') as compiled:
            payload = base64.encodebytes(compiled.read())
        os.remove(tempname)
    except Exception as e:
        print(e)
        return {'error': str(e)}
    return {'compiled': payload}


def home(request):
    ctx = {
        'samplecode': bytecode('sample.py'),
        'othercode': bytecode('other.py'),
    }
    if request.method.lower() == 'post' and request.POST['code']:
        tempfd, tempname = tempfile.mkstemp()
        with os.fdopen(tempfd, 'w+b') as f:
            f.write(bytes(request.POST['code'], 'utf-8'))
            f.flush()

        customcode = {'code': request.POST['code']}
        customcode.update(bytecode(tempname))
        ctx['customcode'] = customcode

        os.remove(tempname)
    return render(request, 'testbed.html', ctx)


urlpatterns = [
    url(r'^$', home),
]
