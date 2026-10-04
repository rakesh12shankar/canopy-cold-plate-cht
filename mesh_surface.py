exec(compile((REPO_DIR/'resource_guard.py').read_text(encoding='utf-8'),'resource_guard.py','exec'),globals())
wait_for_resources(8)
meshing=pyfluent.launch_fluent(product_version='24.1.0',mode='meshing',precision='double',processor_count=1,ui_mode='no_gui_or_graphics',start_timeout=180)
meshing.transcript.start(str(ROOT/f'{CASE}_meshing.trn'))
meshing.workflow.InitializeWorkflow(WorkflowType='Watertight Geometry');workflow=meshing.workflow
workflow.TaskObject['Import Geometry'].Arguments.set_state({'FileName':str(CAD),'LengthUnit':'mm'})
workflow.TaskObject['Import Geometry'].Execute();workflow.TaskObject['Add Local Sizing'].Execute()
workflow.TaskObject['Generate the Surface Mesh'].Arguments.update_dict({'CFDSurfaceMeshControls':{'MinSize':MIN_SIZE,'MaxSize':1.2,'GrowthRate':1.2,'CurvatureNormalAngle':ANGLE}})
workflow.TaskObject['Generate the Surface Mesh'].Execute()
workflow.TaskObject['Describe Geometry'].UpdateChildTasks(SetupTypeChanged=True)
workflow.TaskObject['Describe Geometry'].Arguments.set_state({'CappingRequired':'No','InvokeShareTopology':'Yes','SetupType':'The geometry consists of both fluid and solid regions and/or voids'})
workflow.TaskObject['Describe Geometry'].Execute();workflow.TaskObject['Apply Share Topology'].Execute()
workflow.TaskObject['Update Boundaries'].Execute();workflow.TaskObject['Create Regions'].Execute()
time.sleep(.5)
region_trn=(ROOT/f'{CASE}_meshing.trn').read_text(errors='replace')
region_rows=re.findall(r'^\s*(region\d+)\s+\d+\s+[\d.]+\s+[\d.]+\s+(\d+)\s*$',region_trn,re.M)
region_counts={name:int(count) for name,count in region_rows}
assert len(region_counts)==2, 'Expected exactly two connected CAD regions'
# The plate has the interface plus six exterior faces; the coolant has the
# same interface plus two small ports. Confirm assigned volumes in solver.
region_names=sorted(region_counts,key=region_counts.get,reverse=True)
assert region_counts[region_names[0]]>1.2*region_counts[region_names[1]]
print('DISCOVERED_REGIONS',region_counts,region_names,flush=True)
workflow.TaskObject['Update Regions'].Arguments.set_state({'OldRegionNameList':region_names,'OldRegionTypeList':['solid','solid'],'RegionNameList':['solid_alsi10mg','fluid_water'],'RegionTypeList':['solid','fluid']})
workflow.TaskObject['Update Regions'].Execute()
# Exported body ordering is solid first, fluid second; verify by region volumes later.
meshing.tui.boundary.separate.sep_face_zone_by_angle([12],45)
meshing.tui.boundary.separate.sep_face_zone_by_region([11])
meshing.tui.boundary.manage.list()
time.sleep(.5)
trn=(ROOT/f'{CASE}_meshing.trn').read_text(errors='replace')
rows=re.findall(r'^\s*(\d+)\s+(\S+)\s+wall\s+(\d+)\s+',trn,re.M)[-9:]
assert len(rows)==9,'Unexpected boundary count: inspect before assigning conditions.'
boundaries={}
for zid,name,count in rows:
    before=len(re.findall(r'bounding box dimensions',trn))
    meshing.tui.boundary.compute_bounding_box([int(zid)]);time.sleep(.15)
    trn=(ROOT/f'{CASE}_meshing.trn').read_text(errors='replace')
    boxes=re.findall(r'bounding box dimensions \(\(([^)]+)\) \(([^)]+)\)\)',trn)
    assert len(boxes)>before
    lo=list(map(float,boxes[-1][0].split()));hi=list(map(float,boxes[-1][1].split()))
    if re.fullmatch(r'region\d+-region\d+',name):label='fluid_solid_interface'
    elif abs(lo[2])<1e-4 and abs(hi[2])<1e-4:label='heater_bottom'
    elif abs(lo[2]-10)<1e-4 and abs(hi[2]-10)<1e-4:label='ambient_top'
    elif abs(lo[0])<1e-4 and abs(hi[0])<1e-4:label='side_xmin'
    elif abs(lo[0]-150)<1e-4 and abs(hi[0]-150)<1e-4:label='side_xmax'
    elif abs(lo[1]-150)<1e-4 and abs(hi[1]-150)<1e-4:label='side_ymax'
    elif abs(lo[1])<1e-4 and abs(hi[1])<1e-4:
        if hi[0]-lo[0]>100:label='side_ports'
        elif lo[0]>100:label='inlet'
        elif hi[0]<50:label='outlet'
        else:raise RuntimeError('Unidentified port')
    else:raise RuntimeError('Unidentified boundary '+str((zid,name,lo,hi)))
    assert label not in boundaries,'Duplicate classification'
    boundaries[label]={'id':int(zid),'original_name':name,'lo_mm':lo,'hi_mm':hi}
    meshing.tui.boundary.manage.name(int(zid),label)
assert len(boundaries)==9
meshing.tui.boundary.manage.type([boundaries['inlet']['id']],'velocity-inlet')
meshing.tui.boundary.manage.type([boundaries['outlet']['id']],'pressure-outlet')
(ROOT/f'{CASE}_boundary_checks.json').write_text(json.dumps(boundaries,indent=2))
print('SURFACE_AND_BOUNDARIES_VERIFIED',CASE,flush=True)
