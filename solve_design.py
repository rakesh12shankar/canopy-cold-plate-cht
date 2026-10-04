exec(compile((REPO_DIR/'resource_guard.py').read_text(encoding='utf-8'),'resource_guard.py','exec'),globals())
wait_for_resources(8)
if CASE!='baseline_screen' and (ROOT/'baseline_screen_final_reports.json').exists() and not (ROOT/'seed_fluid_water.ip').exists():
    seed_solver=pyfluent.launch_fluent(product_version='24.1.0',mode='solver',precision='double',processor_count=1,ui_mode='no_gui_or_graphics',start_timeout=180)
    seed_solver.file.read_case_data(file_name=str(ROOT/'baseline_screen.cas.h5'))
    for zone in ['fluid_water','solid_alsi10mg']:
        seed_solver.tui.file.interpolate.zone_selection([zone])
        seed_solver.tui.file.interpolate.write_data('"'+str(ROOT/f'seed_{zone}.ip').replace('\\','/')+'"')
    seed_solver.exit();del seed_solver
solver=pyfluent.launch_fluent(product_version='24.1.0',mode='solver',precision='double',processor_count=1,ui_mode='no_gui_or_graphics',start_timeout=180)
solver.transcript.start(str(ROOT/f'{CASE}_solver.trn'))
solver.file.read_case(file_name=str(ROOT/f'{CASE}_Mesh_SI.cas.h5'))
source=(REPO_DIR/'fluent_setup.py').read_text(encoding='utf-8').split('solver.solution.initialization.hybrid_initialize()')[0]
source=source.replace("flow_scheme='Coupled'",f"flow_scheme='{FLOW_SCHEME}'")
exec(compile(source,'common_cht_physics','exec'),globals())
# Imported meshes do not inherit the earlier baseline's numerical settings.
# Explicitly reuse them so geometry is the controlled comparison variable.
reference_methods=json.loads((ROOT/'baseline_screen_methods.json').read_text()) if (ROOT/'baseline_screen_methods.json').exists() else {
    'discretization_scheme':{'mom':'second-order-upwind','pressure':'second-order','temperature':'second-order-upwind'},
    'gradient_scheme':'least-square-cell-based',
    'warped_face_gradient_correction':{'enable':True,'mode':'fast'}}
if FLOW_SCHEME=='Coupled' and 'p_v_coupling' in reference_methods:
    solver.solution.methods.set_state(reference_methods)
else:
    for key in ['discretization_scheme','gradient_scheme','warped_face_gradient_correction']:
        getattr(solver.solution.methods,key).set_state(reference_methods[key])

for key,state in json.loads((REPO_DIR/'config/water_transport.json').read_text())['properties'].items():
    getattr(solver.setup.materials.fluid['water_benchmark'],key).set_state(state)
extra={'t_base_mean':('surface-areaavg','temperature',['heater_bottom']),
       't_base_max':('surface-facetmax','temperature',['heater_bottom']),
       'pt_in':('surface-massavg','total-pressure',['inlet']),
       'pt_out':('surface-massavg','total-pressure',['outlet'])}
for name,(typ,field,names) in extra.items():
    solver.solution.report_definitions.surface.create(name)
    r=solver.solution.report_definitions.surface[name];r.report_type=typ;r.field=field;r.surface_names=names
reports.update(extra)
for name in ['fluid_water','solid_alsi10mg']:
    report='volume_'+name
    solver.solution.report_definitions.volume.create(report)
    r=solver.solution.report_definitions.volume[report]
    print('VOLUME_TYPES',r.report_type.allowed_values(),flush=True)
    r.report_type='volume-zonevol';r.cell_zones=[name]
volume=solver.solution.report_definitions.compute(report_defs=['volume_fluid_water','volume_solid_alsi10mg'])
vol={k:v[0] for d in volume for k,v in d.items()}
assert .000010<vol['volume_fluid_water']<.000016 and .00020<vol['volume_solid_alsi10mg']<.00022
assert abs(sum(vol.values())/.000225-1)<1e-5
(ROOT/f'{CASE}_volumes.json').write_text(json.dumps(vol,indent=2))
solver.solution.initialization.hybrid_initialize();solver.solution.run_calculation.iterate(iter_count=3)
mass=solver.solution.report_definitions.compute(report_defs=['mass_in'])[0]['mass_in'][0]
peak*=inputs['mass_flow_kg_s']/mass;inlet.momentum.velocity.value=str(peak)+profile
for zone in ['fluid_water','solid_alsi10mg']:
    seed=ROOT/f'seed_{zone}.ip'
    if seed.exists():
        solver.tui.file.interpolate.zone_selection([zone])
        solver.tui.file.interpolate.read_data('ok','"'+str(seed).replace('\\','/')+'"')
if FLOW_SCHEME=='SIMPLEC':
    solver.solution.controls.under_relaxation['pressure']=1.0
    solver.solution.controls.under_relaxation['mom']=.8
else:solver.solution.run_calculation.pseudo_time_settings.time_step_method.time_step_size_scale_factor=1
(ROOT/f'{CASE}_setup.json').write_text(json.dumps(solver.setup.get_state(),indent=2))
(ROOT/f'{CASE}_methods.json').write_text(json.dumps(solver.solution.methods.get_state(),indent=2))
def last_residual(path):
    rows=[]
    for line in path.read_text(errors='replace').splitlines():
        m=re.match(r'^\s*(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+',line)
        if m:rows.append([float(x) for x in m.groups()])
    return rows[-1]
# Native AMG termination is distinct from equation correction tolerance.
solver.scheme_eval.eval("(rpsetvar 'temperature/iter-tolerance 0.05)")
if FLOW_SCHEME=='SIMPLEC':
    mg=solver.solution.controls.advanced.multi_grid.mg_controls
    for equation,state in mg.get_state().items():
        if 'termination_criteria' in state:mg[equation].termination_criteria=.001
    print('AMG_ACTIVE_EQUATIONS_TERMINATION',.001,flush=True)
else:
    print('COUPLED_SCREENING_CONTROLS',flush=True)
(ROOT/f'{CASE}_controls.json').write_text(json.dumps(solver.solution.controls.get_state(),indent=2))
energy_limit=1e-9
solver.solution.monitor.residual.equations['energy'].absolute_criteria=energy_limit
stability_history=[]
for batch in range(30):
    if (ROOT/'checkpoint_handoff').exists():
        raise RuntimeError('Requested control handoff after the last saved checkpoint; no physics changed.')
    control=ROOT/f'{CASE}_numerics.json'
    if control.exists():
        n=json.loads(control.read_text())
        if FLOW_SCHEME=='Coupled':solver.solution.run_calculation.pseudo_time_settings.time_step_method.time_step_size_scale_factor=float(n.get('pseudo_time_factor',1))
        else:
            solver.solution.controls.under_relaxation['pressure']=float(n.get('pressure_urf',1))
            solver.solution.controls.under_relaxation['mom']=float(n.get('momentum_urf',.8))
    solver.solution.run_calculation.iterate(iter_count=40)
    result=solver.solution.report_definitions.compute(report_defs=list(reports)+list(fluxes))
    v={k:a[0] for d in result for k,a in d.items()}
    stability_history.append({'base_mean_K':v['t_base_mean'],'base_max_K':v['t_base_max'],'total_loss_Pa':v['pt_in']-v['pt_out']})
    recent=stability_history[-3:]
    thermal_range={key:max(r[key] for r in recent)-min(r[key] for r in recent) for key in ['base_mean_K','base_max_K']}
    pressure_range=(max(r['total_loss_Pa'] for r in recent)-min(r['total_loss_Pa'] for r in recent))/abs(recent[-1]['total_loss_Pa'])
    stable=len(recent)==3 and max(thermal_range.values())<=1e-4 and pressure_range<=1e-4
    (ROOT/f'{CASE}_reports_{batch+1}.json').write_text(json.dumps(result,indent=2))
    solver.file.write_case_data(file_name=str(ROOT/f'{CASE}.cas.h5'))
    last=last_residual(ROOT/f'{CASE}_solver.trn')
    if stable and max(last[1:5])<=1e-6 and last[5]<=energy_limit and abs(v['mass_net']/v['mass_in'])<1e-4 and abs(v['heat_net'])/200<1e-4:break
else:raise RuntimeError('Design case convergence criteria not met.')
(ROOT/f'{CASE}_final_reports.json').write_text(json.dumps(result,indent=2))
(ROOT/f'{CASE}_convergence.json').write_text(json.dumps({'residual':last,'energy_residual_limit':energy_limit,'mass_imbalance_pct':100*abs(v['mass_net']/v['mass_in']),'heat_imbalance_pct':100*abs(v['heat_net'])/200,'last_three_checkpoints':recent,'temperature_stability_range_K':thermal_range,'total_pressure_stability_fraction':pressure_range},indent=2))
print('DESIGN_CASE_CONVERGED',CASE,v,flush=True)
