from pathlib import Path

def write_pipe(path,nx,nr,length=.1,radius=.003):
    # Fluent ASCII face mesh; each directed edge has cell c0 on its left.
    node=lambda i,j:1+j*(nx+1)+i
    cell=lambda i,j:1+j*nx+i
    groups={3:[],4:[],5:[],6:[],7:[]}
    for j in range(nr):
        for i in range(nx):
            c=cell(i,j)
            if j==0: groups[4].append((node(i,0),node(i+1,0),c,0))
            else: groups[3].append((node(i,j),node(i+1,j),c,cell(i,j-1)))
            if i==nx-1: groups[6].append((node(nx,j),node(nx,j+1),c,0))
            else: groups[3].append((node(i+1,j),node(i+1,j+1),c,cell(i+1,j)))
            if j==nr-1: groups[7].append((node(i+1,nr),node(i,nr),c,0))
            if i==0: groups[5].append((node(0,j+1),node(0,j),c,0))
    nn=(nx+1)*(nr+1);nf=sum(map(len,groups.values()));nc=nx*nr
    lines=['(0 "Structured axisymmetric pipe; SI meters")','(2 2)',f'(10 (0 1 {nn:x} 0 2))',f'(12 (0 1 {nc:x} 0))',f'(13 (0 1 {nf:x} 0))',f'(10 (1 1 {nn:x} 1 2)(']
    lines += [f'{length*i/nx:.16e} {radius*j/nr:.16e}' for j in range(nr+1) for i in range(nx+1)]
    lines+=['))',f'(12 (2 1 {nc:x} 1 3))','(45 (2 fluid water)())']
    start=1
    for zone,faces in groups.items():
        typ,name={3:(2,'interior'),4:(37,'axis'),5:(10,'inlet'),6:(5,'outlet'),7:(3,'heated_wall')}[zone]
        lines.append(f'(13 ({zone:x} {start:x} {start+len(faces)-1:x} {typ:x} 2)(')
        lines += [' '.join(f'{v:x}' for v in face) for face in faces]
        lines+=['))',f'(45 ({zone} { {2:"interior",37:"axis",10:"velocity-inlet",5:"pressure-outlet",3:"wall"}[typ]} {name})())']
        start+=len(faces)
    Path(path).write_text('\n'.join(lines)+'\n',encoding='ascii')

if __name__=='__main__':
    root=Path(__file__).resolve().parent/'.generated/pipe'
    root.mkdir(parents=True,exist_ok=True)
    for name,nx,nr in [('coarse',100,20),('medium',200,40),('fine',400,80)]: write_pipe(root/f'pipe_{name}.msh',nx,nr)
