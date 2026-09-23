import sys,os
from pyctr.type.cia import CIAReader
from pyctr.type.ncch import NCCHSection
cia,out=sys.argv[1],sys.argv[2]
with CIAReader(cia) as c:
    n=c.contents[0]
    with n.open_raw_section(NCCHSection.FullDecrypted) as f, open(out,'wb') as o:
        while True:
            b=f.read(1<<24)
            if not b: break
            o.write(b)
print('ok',os.path.getsize(out))
