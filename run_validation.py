"""Audit supplied compact records against physical and numerical criteria."""
from pathlib import Path
import json, math
ROOT=Path(__file__).resolve().parent

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))

def main():
    records=load('results/reference/design_results.json')
    names={r['case'] for r in records}
    assert {'baseline_refined','baseline_screen','inlet7_screen','outlet7_screen'}<=names
    rho=load('config/physics.json')['water']['density']
    for r in records:
        c=r['convergence'];res=c.get('residual',c.get('last_residual'))
        assert max(res[1:5])<=1e-6 and res[5]<=1e-9,r['case']
        assert c['mass_imbalance_pct']<.01 and c['heat_imbalance_pct']<.01,r['case']
        assert math.isclose(r['hydraulic_power_W'],r['mass_flow_kg_h']/3600/rho*r['total_pressure_loss_Pa'],rel_tol=1e-10)
        assert math.isclose(r['R_base_mean_K_W'],(r['base_mean_C']-23)/200,abs_tol=1e-12)
        if r['case']!='baseline_refined':
            assert max(c['temperature_stability_range_K'].values())<=1e-4
            assert c['total_pressure_stability_fraction']<=1e-4
        if r['case'].endswith('_equal_power'):assert abs(c['power_error_pct'])<=.5
    audit=load('results/reference/physics_audit.json')
    assert len(audit)==2 and all(all(r['identical_physics'].values()) for r in audit)
    for p in (ROOT/'results/reference/records').glob('*_mesh_checks.json'):
        m=json.loads(p.read_text());assert min(m['minimum_orthogonal_quality'].values())>.1
        assert m['layers']==(8 if '_refined' in p.name else 5)
    pipe=load('results/reference/pipe_verification.json');assert len(pipe)==3
    for r in pipe:
        assert math.isclose(r['cfd_interior_dp_Pa'],r['raw_reports']['p_up']-r['raw_reports']['p_down'],rel_tol=1e-12)
        assert math.isclose(r['pressure_error_pct'],100*(r['cfd_interior_dp_Pa']/r['analytical_interior_dp_Pa']-1),abs_tol=1e-10)
        assert math.isclose(r['bulk_rise_error_pct'],100*(r['cfd_bulk_rise_K']/r['analytical_bulk_rise_K']-1),abs_tol=1e-10)
    fine=pipe[-1];assert abs(fine['pressure_error_pct'])<.04 and abs(fine['bulk_rise_error_pct'])<.04
    print(f'PASS: {len(records)} CHT records, matched screening physics, mesh quality/layers, pressure/power/resistance definitions, and three analytical pipe records.')
    print('This is an audit of numerical evidence; it does not establish experimental validation or cold-plate mesh independence.')

if __name__=='__main__':main()
