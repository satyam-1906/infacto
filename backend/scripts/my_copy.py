import os, shutil
u = os.environ['USERPROFILE']
path = os.path.join(u, '.gemini', 'antigravity', 'brain', 'fce06eef-14f0-4e73-ae37-93589195b4dc', 'media__1786469135986.jpg')
shutil.copyfile(path, 'qr_code.jpg')
