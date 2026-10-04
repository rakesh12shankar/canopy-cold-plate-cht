"""Regenerate comparison tables and figures from supplied numerical records."""
from pathlib import Path
import argparse,csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.generated/analysis')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    records=json.loads((ROOT/'results/reference/design_results.json').read_text())
    columns=['case','cells','mass_flow_kg_h','base_mean_C','base_max_C','R_base_mean_K_W','R_base_max_K_W','static_dp_Pa','total_pressure_loss_Pa','hydraulic_power_W','top_mean_C','top_max_C','outlet_bulk_C']
    with (args.output/'design_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(records)
    screen=[r for r in records if r['case'].endswith('_screen')]
    baseline=next(r for r in screen if r['case']=='baseline_screen')
    order=['baseline_screen','inlet7_screen','outlet7_screen']
    screen=sorted(screen,key=lambda r:order.index(r['case']))
    labels=['Baseline','Inlet D7','Outlet D7']
    fig,axes=plt.subplots(1,2,figsize=(10,4.6))
    axes[0].bar(labels,[r['hydraulic_power_W']*1000 for r in screen],color=['#657b8d','#dc883b','#277c9e'])
    axes[0].set_ylabel('Hydraulic power (mW)');axes[0].set_title('Equal flow: 22.3 kg/h')
    x=list(range(3))
    axes[1].bar([a-.18 for a in x],[r['base_mean_C']-baseline['base_mean_C'] for r in screen],width=.36,label='Area mean')
    axes[1].bar([a+.18 for a in x],[r['base_max_C']-baseline['base_max_C'] for r in screen],width=.36,label='Maximum')
    axes[1].set_xticks(x,labels);axes[1].axhline(0,color='#555',lw=.8)
    axes[1].set_ylabel('Heated-base temperature change (K)');axes[1].set_title('Relative to screening baseline');axes[1].legend()
    for ax in axes:ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    fig.suptitle('Controlled manifold screening: 200 W, 23 °C inlet')
    fig.text(.5,.025,'Screening mesh only. Enlarged manifolds add ~9.6% coolant volume and reduce minimum cover to 1.5 mm.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(args.output/'manifold_screening.png',dpi=180);plt.close(fig)
    refined=[r for r in records if r['case']=='baseline_refined' or r['case'].endswith('_refined') or r['case'].endswith('_equal_power')]
    if len(refined)==3:
        fig,axes=plt.subplots(1,2,figsize=(10,4.7));labels=['Baseline','Outlet D7\nequal flow','Outlet D7\nequal power']
        refined.sort(key=lambda r:0 if r['case']=='baseline_refined' else 2 if r['case'].endswith('_equal_power') else 1)
        for r,label in zip(refined,labels):axes[0].scatter(r['hydraulic_power_W']*1000,r['base_max_C'],s=65,label=label.replace('\n',' '))
        axes[0].set_xlabel('Hydraulic power (mW)');axes[0].set_ylabel('Maximum heated-base temperature (°C)');axes[0].legend(fontsize=8)
        axes[1].bar(labels,[r['mass_flow_kg_h'] for r in refined],color=['#657b8d','#dc883b','#277c9e']);axes[1].set_ylabel('Flow (kg/h)')
        for ax in axes:ax.grid(alpha=.2);ax.set_axisbelow(True)
        fig.suptitle('Refined manifold confirmation and equal-power comparison')
        fig.text(.5,.025,'Numerical comparisons; overall cold-plate mesh independence and experimental validation are not established.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.06,1,.94));fig.savefig(args.output/'manifold_refined.png',dpi=180);plt.close(fig)
    print('Recreated compact tables and available figures in',args.output)

if __name__=='__main__':main()
