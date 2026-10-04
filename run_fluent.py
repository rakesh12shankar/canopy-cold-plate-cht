"""Run a new licensed CFD calculation without overwriting archived evidence.

Recorded platform: Windows, Fluent 2024 R1, double precision, one process.
Use one invocation at a time. The resource guard waits for other Fluent jobs.
"""
from pathlib import Path
import argparse, json, os, re, time
import ansys.fluent.core as pyfluent

REPO_DIR=Path(__file__).resolve().parent
ROOT=REPO_DIR/'.generated/fluent'
BASE=ROOT.parent
PREV=None

def helper(name):
    exec(compile((REPO_DIR/name).read_text(encoding='utf-8'),name,'exec'),globals())

def main():
    global CASE,CAD,MIN_SIZE,MAX_SIZE,ANGLE,LAYERS,FLOW_SCHEME,solver,inputs,peak,profile,reports,fluxes,target_power_W
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=['baseline_screen','inlet7_screen','outlet7_screen','outlet7_refined','inlet7_refined'],required=True)
    parser.add_argument('--equal-power',action='store_true',help='Continue the converged refined case at archived refined-baseline hydraulic power')
    args=parser.parse_args()
    if args.equal_power and not args.case.endswith('_refined'):
        parser.error('--equal-power requires a refined variant')
    if os.name!='nt':parser.error('This recorded meshing/resource workflow targets Windows')
    ROOT.mkdir(parents=True,exist_ok=True)
    os.chdir(ROOT)
    CASE=args.case
    FLOW_SCHEME='Coupled' if CASE.endswith('_screen') else 'SIMPLEC'
    refined=CASE.endswith('_refined')
    helper('resource_guard.py');wait_for_resources(12 if refined else 8)
    reference_methods=REPO_DIR/'config/screening_methods.json'
    (ROOT/'baseline_screen_methods.json').write_text(reference_methods.read_text(encoding='utf-8'),encoding='utf-8')
    try:
        if not args.equal_power:
            if (ROOT/f'{CASE}_final_reports.json').exists():
                print('Converged generated case retained. Use a new output directory to rerun.');return
            variant=CASE.split('_')[0]
            names={'baseline':'Canopy_4Branch_CHT.x_t','inlet7':'Canopy_Inlet7_CHT.x_t','outlet7':'Canopy_Outlet7_CHT.x_t'}
            CAD=REPO_DIR/'data/cad'/variant/names[variant]
            MIN_SIZE=.09 if refined else .16;MAX_SIZE=1.2;ANGLE=9 if refined else 18;LAYERS=8 if refined else 5
            if not (ROOT/f'{CASE}_Mesh_SI.cas.h5').exists():
                helper('mesh_surface.py');helper('mesh_volume.py')
            helper('solve_design.py')
        else:
            assert (ROOT/f'{CASE}_convergence.json').exists(),'Converge the generated equal-flow case first'
            target_power_W=json.loads((REPO_DIR/'config/reference_power.json').read_text())['hydraulic_power_W']
            inputs=json.loads((REPO_DIR/'config/physics.json').read_text())
            solver=pyfluent.launch_fluent(product_version='24.1.0',mode='solver',precision='double',processor_count=1,ui_mode='no_gui_or_graphics',start_timeout=180)
            solver.file.read_case_data(file_name=str(ROOT/f'{CASE}.cas.h5'))
            inlet=solver.setup.boundary_conditions.velocity_inlet['inlet']
            profile=' [m/s] * (1-((x-0.125[m])**2+(z-0.005[m])**2)/(0.003[m])**2)'
            peak=float(inlet.momentum.velocity.value().split(' [m/s]')[0])
            reports={name:None for name in ['t_top_mean','t_top_max','t_out_mass','p_in','p_out','t_base_mean','t_base_max','pt_in','pt_out']}
            fluxes={name:None for name in ['mass_in','mass_net','heat_net']}
            def last_residual(path):
                rows=[]
                for line in path.read_text(errors='replace').splitlines():
                    m=re.match(r'^\s*(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+',line)
                    if m:rows.append([float(x) for x in m.groups()])
                return rows[-1]
            globals()['last_residual']=last_residual
            helper('equal_power.py')
    finally:
        if 'solver' in globals():
            try:solver.exit()
            except Exception:pass
    print('New calculation saved in',ROOT)

if __name__=='__main__':main()
