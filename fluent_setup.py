inputs=json.loads((REPO_DIR/'config/physics.json').read_text())
solver.setup.models.energy.enabled=True
solver.setup.models.viscous.model='laminar'
solver.setup.materials.fluid.create('water_benchmark')
for key,value in inputs['water'].items():
    getattr(solver.setup.materials.fluid['water_benchmark'],key).set_state({'option':'constant','value':value})
solver.setup.cell_zone_conditions.fluid['fluid_water'].material='water_benchmark'
solver.setup.materials.solid.create('alsi10mg_benchmark')
al=solver.setup.materials.solid['alsi10mg_benchmark']
al.density.value=2590
al.specific_heat.value=915
al.thermal_conductivity.option='anisotropic'
al.thermal_conductivity.anisotropic.conductivity.value=123.4
al.thermal_conductivity.anisotropic.matrix_component=[1,0,0,0,1,0,0,0,131/123.4]
solver.setup.cell_zone_conditions.solid['solid_alsi10mg'].material='alsi10mg_benchmark'
inlet=solver.setup.boundary_conditions.velocity_inlet['inlet']
peak=2*inputs['mean_inlet_velocity_m_s']
profile=' [m/s] * (1-((x-0.125[m])**2+(z-0.005[m])**2)/(0.003[m])**2)'
inlet.momentum.velocity.value=str(peak)+profile
inlet.thermal.t.value=296.15
solver.setup.boundary_conditions.pressure_outlet['outlet'].thermal.t0.value=296.15
heater=solver.setup.boundary_conditions.wall['heater_bottom']
heater.thermal.thermal_bc='Heat Flux'
heater.thermal.q.value=inputs['heat_flux_W_m2']
solver.setup.named_expressions.create('RaTop')
solver.setup.named_expressions['RaTop'].definition=str(inputs['Ra_per_kelvin'])+' [K^-1] * IF(StaticTemperature > 297.15[K], StaticTemperature - 297.15[K], 0[K])'
top=solver.setup.boundary_conditions.wall['ambient_top']
top.thermal.thermal_bc='Convection'
top.thermal.tinf.value=297.15
top.thermal.h.value=str(inputs['air']['thermal_conductivity'])+' [W m^-1 K^-1]/0.15[m] * IF(RaTop < 1.5e6, 1.65*RaTop**0.175, IF(RaTop < 8e7, 0.58*RaTop**0.25, 0.135*RaTop**0.33))'
reports={
 't_top_mean':('surface-areaavg','temperature',['ambient_top']),
 't_top_max':('surface-facetmax','temperature',['ambient_top']),
 't_top_min':('surface-facetmin','temperature',['ambient_top']),
 't_out_mass':('surface-massavg','temperature',['outlet']),
 't_out_area':('surface-areaavg','temperature',['outlet']),
 'p_in':('surface-areaavg','pressure',['inlet']),
 'p_out':('surface-areaavg','pressure',['outlet'])}
fluxes={
 'mass_in':('flux-massflow',['inlet']),
 'mass_out':('flux-massflow',['outlet']),
 'mass_net':('flux-massflow',['inlet','outlet']),
 'heat_bottom':('flux-heattransfer',['heater_bottom']),
 'heat_top':('flux-heattransfer',['ambient_top']),
 'heat_net':('flux-heattransfer',['inlet','outlet','heater_bottom','ambient_top','side_xmin','side_xmax','side_ymax','side_ports'])}
for name,(typ,field,surfaces) in reports.items():
    solver.solution.report_definitions.surface.create(name)
    r=solver.solution.report_definitions.surface[name]
    r.report_type=typ
    r.field=field
    r.surface_names=surfaces
for name,(typ,bounds) in fluxes.items():
    solver.solution.report_definitions.flux.create(name)
    r=solver.solution.report_definitions.flux[name]
    r.report_type=typ
    r.boundaries=bounds
for name in ['continuity','x-velocity','y-velocity','z-velocity']:
    solver.solution.monitor.residual.equations[name].absolute_criteria=1e-6
solver.solution.monitor.residual.equations['energy'].absolute_criteria=1e-9
solver.solution.methods.p_v_coupling.flow_scheme='Coupled'
