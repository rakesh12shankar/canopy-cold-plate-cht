import math
solver.setup.general.solver.two_dim_space='axisymmetric'
solver.setup.models.energy.enabled=True
solver.setup.models.viscous.model='laminar'
water=json.loads((REPO_DIR/'config/physics.json').read_text())['water']
solver.setup.materials.fluid.create('water_benchmark')
for key,value in water.items():getattr(solver.setup.materials.fluid['water_benchmark'],key).set_state({'option':'constant','value':value})
solver.setup.cell_zone_conditions.fluid['water'].material='water_benchmark'
inlet=solver.setup.boundary_conditions.velocity_inlet['inlet']
inlet.momentum.velocity.value='0.2 [m/s]*(1-(y/0.003[m])**2)'
inlet.thermal.t.value=296.15
solver.setup.boundary_conditions.pressure_outlet['outlet'].thermal.t0.value=296.15
wall=solver.setup.boundary_conditions.wall['heated_wall']
wall.thermal.thermal_bc='Heat Flux';wall.thermal.q.value=5000
for name,x in [('pressure_up',.02),('pressure_down',.08)]:
    solver.results.surfaces.iso_surface.create(name)
    solver.results.surfaces.iso_surface[name].set_state({'field':'x-coordinate','zones':['water'],'iso_values':[x]})
reports={
 'p_in':('surface-areaavg','pressure',['inlet']),
 'p_out':('surface-areaavg','pressure',['outlet']),
 'p_up':('surface-areaavg','pressure',['pressure_up']),
 'p_down':('surface-areaavg','pressure',['pressure_down']),
 't_out':('surface-massavg','temperature',['outlet'])}
fluxes={'mass_in':('flux-massflow',['inlet']),'mass_net':('flux-massflow',['inlet','outlet']),
        'heat_wall':('flux-heattransfer',['heated_wall']),'heat_net':('flux-heattransfer',['inlet','outlet','heated_wall'])}
for name,(typ,field,names) in reports.items():
    solver.solution.report_definitions.surface.create(name)
    r=solver.solution.report_definitions.surface[name];r.report_type=typ;r.field=field;r.surface_names=names
for name,(typ,names) in fluxes.items():
    solver.solution.report_definitions.flux.create(name)
    r=solver.solution.report_definitions.flux[name];r.report_type=typ;r.boundaries=names
for name in ['continuity','x-velocity','y-velocity']:solver.solution.monitor.residual.equations[name].absolute_criteria=1e-8
solver.solution.monitor.residual.equations['energy'].absolute_criteria=1e-10
solver.solution.methods.p_v_coupling.flow_scheme='Coupled'
solver.solution.methods.discretization_scheme={'mom':'second-order-upwind','pressure':'second-order','temperature':'second-order-upwind'}
solver.solution.initialization.hybrid_initialize()
for batch in range(20):
    solver.solution.run_calculation.iterate(iter_count=50)
    result=solver.solution.report_definitions.compute(report_defs=list(reports)+list(fluxes))
    v={k:a[0] for d in result for k,a in d.items()}
    residual=[]
    for line in (ROOT/f'pipe_{CASE}.trn').read_text(errors='replace').splitlines():
        m=re.match(r'^\s*(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+',line)
        if m:residual=[float(x) for x in m.groups()]
    assert residual,'No residual history found.'
    if max(residual[1:4])<=1e-8 and residual[4]<=1e-10 and abs(v['mass_net']/v['mass_in'])<1e-6 and abs(v['heat_net'])<1e-4:break
else:raise RuntimeError('Pipe convergence criteria not met.')
rho=water['density'];mu=water['viscosity'];cp=water['specific_heat'];R=.003;L=.1
mean=v['mass_in']/(rho*math.pi*R*R)
dp=8*mu*.06*mean/(R*R)
q=5000*2*math.pi*R*L
rise=q/(v['mass_in']*cp)
answer={'mesh':CASE,'nx':NX,'nr':NR,'cells':NX*NR,'residual':residual,
 'mass_flow_kg_s':v['mass_in'],'nominal_mean_velocity_m_s':.1,'achieved_mean_velocity_m_s':mean,
 'flow_error_pct':100*(mean/.1-1),'Re':rho*mean*2*R/mu,
 'analytical_interior_dp_Pa':dp,'cfd_interior_dp_Pa':v['p_up']-v['p_down'],
 'pressure_error_pct':100*((v['p_up']-v['p_down'])/dp-1),
 'analytical_heat_W':q,'cfd_heat_W':v['heat_wall'],
 'analytical_bulk_rise_K':rise,'cfd_bulk_rise_K':v['t_out']-296.15,
 'bulk_rise_error_pct':100*((v['t_out']-296.15)/rise-1),
 'mass_imbalance_pct':100*abs(v['mass_net']/v['mass_in']),
 'heat_imbalance_pct':100*abs(v['heat_net'])/q,'raw_reports':v}
(ROOT/f'pipe_{CASE}_results.json').write_text(json.dumps(answer,indent=2))
solver.file.write_case_data(file_name=str(ROOT/f'pipe_{CASE}.cas.h5'))
print('PIPE_VERIFIED',answer,flush=True)
