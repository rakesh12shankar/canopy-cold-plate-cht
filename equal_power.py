"""Continue a converged refined variant at the refined baseline hydraulic power.

Requires globals solver, ROOT, CASE, inputs, reports, fluxes, profile, peak,
last_residual, and target_power_W. Dynamic-flow iteration is excluded from
the final fixed-boundary convergence test.
"""
rho=inputs['water']['density']
inlet=solver.setup.boundary_conditions.velocity_inlet['inlet']
original=CASE
CASE=original+'_equal_power'
solver.transcript.stop()
solver.transcript.start(str(ROOT/f'{CASE}_solver.trn'))
history=[]
for adjustment in range(12):
    result=solver.solution.report_definitions.compute(report_defs=['mass_in','pt_in','pt_out'])
    v={k:a[0] for d in result for k,a in d.items()}
    power=abs(v['mass_in'])/rho*(v['pt_in']-v['pt_out'])
    assert power>0
    error=power/target_power_W-1
    history.append({'phase':'flow_adjustment','step':adjustment,'mass_flow_kg_s':v['mass_in'],'hydraulic_power_W':power,'power_error_pct':100*error})
    if abs(error)<.001:break
    factor=max(.95,min(1.05,(target_power_W/power)**.5))
    peak*=factor
    inlet.momentum.velocity.value=str(peak)+profile
    solver.solution.run_calculation.iterate(iter_count=60)
else:raise RuntimeError('Equal-power flow adjustment did not settle within 0.1%')
stability_history=[]
for batch in range(40):
    solver.solution.run_calculation.iterate(iter_count=40)
    result=solver.solution.report_definitions.compute(report_defs=list(reports)+list(fluxes))
    v={k:a[0] for d in result for k,a in d.items()}
    power=abs(v['mass_in'])/rho*(v['pt_in']-v['pt_out'])
    last=last_residual(ROOT/f'{CASE}_solver.trn')
    stability_history.append({'base_mean_K':v['t_base_mean'],'base_max_K':v['t_base_max'],'total_loss_Pa':v['pt_in']-v['pt_out']})
    recent=stability_history[-3:]
    thermal_range={key:max(r[key] for r in recent)-min(r[key] for r in recent) for key in ['base_mean_K','base_max_K']}
    pressure_range=(max(r['total_loss_Pa'] for r in recent)-min(r['total_loss_Pa'] for r in recent))/abs(recent[-1]['total_loss_Pa'])
    stable=len(recent)==3 and max(thermal_range.values())<=1e-4 and pressure_range<=1e-4
    history.append({'phase':'fixed_flow_convergence','batch':batch,'residual':last,'mass_flow_kg_s':v['mass_in'],'hydraulic_power_W':power,'power_error_pct':100*(power/target_power_W-1)})
    (ROOT/f'{CASE}_history.json').write_text(json.dumps(history,indent=2))
    solver.file.write_case_data(file_name=str(ROOT/f'{CASE}.cas.h5'))
    if stable and max(last[1:5])<=1e-6 and last[5]<=1e-9 and abs(v['mass_net']/v['mass_in'])<1e-4 and abs(v['heat_net'])/200<1e-4:
        if abs(power/target_power_W-1)>.005:
            raise RuntimeError('Converged equal-power mismatch exceeds 0.5%; correct flow and reconverge')
        break
else:raise RuntimeError('Equal-power fixed-flow convergence not achieved')
(ROOT/f'{CASE}_final_reports.json').write_text(json.dumps(result,indent=2))
(ROOT/f'{CASE}_convergence.json').write_text(json.dumps({'residual':last,'mass_imbalance_pct':100*abs(v['mass_net']/v['mass_in']),'heat_imbalance_pct':100*abs(v['heat_net'])/200,'target_power_W':target_power_W,'achieved_power_W':power,'power_error_pct':100*(power/target_power_W-1),'fixed_inlet_peak_m_s':peak,'last_three_checkpoints':recent,'temperature_stability_range_K':thermal_range,'total_pressure_stability_fraction':pressure_range},indent=2))
print('EQUAL_POWER_CONVERGED',CASE,v,flush=True)
