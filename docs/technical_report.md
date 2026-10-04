# Canopy cold-plate conjugate heat-transfer study

## Research question

Can increasing one internal manifold diameter reduce resistance and heated-base temperature at fixed flow, and can the resistance benefit improve cooling at fixed hydraulic power? The independent numerical design study can proceed without the paper authors' exact CAD. Its literature comparison remains a reconstruction with explicitly missing inputs.

## Geometry and source separation

The reference is Guil-Pedrosa et al., International Journal of Thermal Sciences 214 (2025), 109918, [DOI](https://doi.org/10.1016/j.ijthermalsci.2025.109918). Table 2's Mesh 5 N4 case supplies rounded comparison values: 22.3 kg/h, inlet 23 °C, 200 W, ambient 24 °C; static pressure difference 81.3 Pa, top mean/max 37.7/42.9 °C and outlet 31.2 °C. The outlet averaging method is unspecified. These numbers do not prescribe all geometry and solver implementation details.

Reconstructed plate: 150 × 150 × 10 mm, D6 trunks at x=25/125 mm and z=5 mm. Four branches connect the trunks at y=25,58.333333,91.666667,125 mm, with diameters 3.1,3.7,4.4,4.9 mm. Sharp unions and flat terminal faces are retained. Exact original fillets, unrounded dimensions and material functions are unavailable.

Inlet7/Outlet7 enlarge the selected internal trunk to D7 over y=10–125 mm, retaining the D6 external port. Plate dimensions and branches are fixed. Coolant CAD volume rises approximately 9.6%; minimum nominal cover decreases from 2 to 1.5 mm. The sharp diameter step is a design assumption. No structural or manufacturing qualification is performed.

## Physical model

Steady 3D pressure-based laminar CHT, double precision, no gravity. Fluid/solid interfaces are coupled and conformal; walls are no-slip. Water viscosity and conductivity use CoolProp HEOS tables at atmospheric pressure over 15–60 °C. Density and cp remain fixed at 23 °C. Anisotropic solid k is 123.4/123.4/131 W/(m K), density 2590 kg/m³ and cp 915 J/(kg K).

The inlet has a parabolic circular profile calibrated to integrated 22.3 kg/h; inlet/backflow temperatures are 296.15 K. Outlet gauge pressure is zero. Bottom heat flux is 8888.8889 W/m², giving 200 W on 0.0225 m². Top ambient is 297.15 K with the source's piecewise natural-convection correlation and fixed 304 K air properties; remaining external surfaces are adiabatic. `config/physics.json` and `water_transport.json` contain executable inputs, including assumptions.

## Numerical verification and definitions

Screening: polyhedral mesh, 0.16–1.2 mm size, curvature 18°, five prism layers at growth 1.2. Confirmation: 0.09–1.2 mm, curvature 9°, eight layers, matching the prior refined baseline's settings. Discretization is second-order pressure/momentum/temperature, least-square gradients, with warped-face correction. Screening uses Coupled; confirmation uses SIMPLEC with tighter active-equation AMG termination. The earlier algorithm comparison showed negligible physical changes at checked converged conditions.

New cases require continuity/momentum residuals ≤1e-6, energy ≤1e-9, mass and heat imbalances <0.01%, and three saved checkpoints with base mean/max ranges ≤0.0001 K and total-pressure-loss range ≤0.01%. The equal-power procedure adjusts flow, freezes the inlet, then reconverges with these checks and ≤0.5% power mismatch. Saved checkpoints may be separated by fewer iterations when Fluent meets its stopping criteria.

Hydraulic power is `abs(mdot)/rho × (mass-weighted inlet total pressure − mass-weighted outlet total pressure)`. It excludes external loop losses and pump efficiency. Static pressure difference is a separate area-average metric. Heated-base resistance is `(base temperature − inlet temperature)/200 W`, using area mean or face maximum as labeled. The paper's top temperatures remain separate.

The analytical pipe case uses an axisymmetric R3 mm, L100 mm pipe, nominal mean U0.1 m/s, inlet 23 °C and wall heat flux 5000 W/m². Three meshes verify interior Poiseuille pressure loss and bulk energy, using each mesh's actual integrated flow. Finest errors are below 0.04%; the energy comparison neglects axial conduction while Fluent retains it. This does not experimentally validate the CHT plate.

## Findings and remaining uncertainty

The refined equal-flow and equal-power comparisons are complete.

The screening outlet enlargement reduces hydraulic power 10.497% and changes maximum base temperature -1.0749 K. At equal flow, the refined outlet variant changes hydraulic power by -10.252% and maximum heated-base temperature by -1.0103 K. At the refined baseline hydraulic power, achieved flow is 23.2010 kg/h; heated-base mean/max change by -0.5921 / -1.4146 K. These are numerical comparisons with volume/cover tradeoffs, rather than experimentally validated hardware improvements.

The outlet's equal-flow mean/max temperature benefit changes from -0.3489/-1.0749 K on screening meshes to -0.2222/-1.0103 K on refined meshes. Hydraulic-power reduction changes from 10.497% to 10.252%. The maximum-temperature and power benefits persist across these two resolutions; the smaller mean-temperature benefit is more sensitive. This comparison mixes mesh and algorithm changes, so it is sensitivity evidence, not a formal discretization-error estimate or confidence interval.

The refined reconstruction gives static Δp91.0363 Pa and top mean/max39.2829/44.1829 °C: +11.98% pressure, +1.583 K mean and +1.283 K maximum relative to the rounded source values. This discrepancy is preserved. No parameter fitting is used to claim source reproduction.

The prior layer/surface sensitivity changes oppose one another. No cold-plate GCI or overall mesh-independence claim is made. Screening curved-wall faceting lowers baseline mesh coolant volume roughly 5% versus CAD. Section diagnostics retain area, flow-closure and within-branch interpolation checks. Refined baseline midbranch Reynolds numbers are 507–618, consistent with laminar branches but insufficient to exclude junction recirculation or unsteadiness. Exact source CAD/material functions and raw data remain unavailable.

The load is 0.889 W/cm² over the footprint. This is a thermal-fluid portfolio study, not a demonstrated high-heat-flux compute-hardware cooling product.

## Reproducibility

See [commands and evidence map](reproducibility.md). Original geometry, numerical records and regenerated plots are included. Publisher PDFs, author correspondence, development transcripts, machine/license settings and full native solver binaries are excluded from this source package. Ansys licensing is required for new CFD runs. Source automation and documentation were prepared with AI assistance and checked against saved numerical evidence. No open-source reuse license is selected.
