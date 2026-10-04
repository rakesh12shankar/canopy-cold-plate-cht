"""Recreate the independent three-grid pipe check with licensed Fluent."""
from pathlib import Path
import argparse,json,re,time,os
import ansys.fluent.core as pyfluent
from build_pipe_mesh import write_pipe
REPO_DIR=Path(__file__).resolve().parent
ROOT=REPO_DIR/'.generated/pipe'

def main():
    global CASE,NX,NR,solver
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh',choices=['coarse','medium','fine','all'],default='all')
    args=parser.parse_args();ROOT.mkdir(parents=True,exist_ok=True)
    if os.name!='nt':parser.error('The recorded resource guard targets Windows')
    exec(compile((REPO_DIR/'resource_guard.py').read_text(encoding='utf-8'),'resource_guard.py','exec'),globals())
    wait_for_resources(2)
    for CASE,NX,NR in [('coarse',100,20),('medium',200,40),('fine',400,80)]:
        if args.mesh not in ['all',CASE]:continue
        mesh=ROOT/f'pipe_{CASE}.msh';write_pipe(mesh,NX,NR)
        solver=pyfluent.launch_fluent(product_version='24.1.0',mode='solver',dimension=2,precision='double',processor_count=1,ui_mode='no_gui_or_graphics',start_timeout=180)
        try:
            solver.transcript.start(str(ROOT/f'pipe_{CASE}.trn'))
            solver.file.read_mesh(file_name=str(mesh));solver.tui.mesh.check()
            exec(compile((REPO_DIR/'solve_pipe.py').read_text(encoding='utf-8'),'solve_pipe.py','exec'),globals())
        finally:solver.exit()
    print('Independent regenerated pipe results saved in',ROOT)

if __name__=='__main__':main()
