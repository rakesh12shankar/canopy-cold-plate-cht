param([string]$OutputDirectory = $PSScriptRoot)
$ErrorActionPreference = 'Stop'
$interop = 'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SolidWorks.Interop.sldworks.dll'
Add-Type -Path $interop
Add-Type -ReferencedAssemblies $interop -TypeDefinition @'
using System;
using System.IO;
using System.Text;
using SolidWorks.Interop.sldworks;
public class Outlet7Cad {
 static IModeler modeler;
 static StringBuilder report=new StringBuilder();
 static IBody2 Cylinder(double x,double y,double z,double ax,double ay,double az,double radius,double length){
  IBody2 b=(IBody2)modeler.CreateBodyFromCyl(new double[]{x,y,z,ax,ay,az,radius,length});
  if(b==null)throw new Exception("Cylinder construction failed"); return b;
 }
 static IBody2 Op(IBody2 a,IBody2 b,int op){
  int error;
  object[] result=(object[])a.Operations2(op,b,out error);
  if(error!=0 || result==null || result.Length!=1)throw new Exception("Boolean operation failed or did not yield one body: "+error);
  return (IBody2)result[0];
 }
 static double Volume(IBody2 b){return ((double[])b.GetMassProperties(1))[3];}
 static void Save(IModelDoc2 doc,string name){
  int error=0,warning=0;
  doc.ClearSelection2(true);
  if(!doc.Extension.SaveAs(name,0,1,null,ref error,ref warning) || error!=0)throw new Exception("Save failed "+name+" error="+error);
  report.AppendLine("Saved "+Path.GetFileName(name)+"; warning code="+warning);
 }
 static IModelDoc2 Document(ISldWorks app,string dir,string name,IBody2[] bodies,string[] names){
  string template=@"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2019\templates\Part.prtdot";
  IModelDoc2 doc=(IModelDoc2)app.NewDocument(template,0,0,0);
  if(doc==null)throw new Exception("Could not create part");
  IPartDoc part=(IPartDoc)doc;
  for(int i=0;i<bodies.Length;i++){
   IFeature f=(IFeature)part.CreateFeatureFromBody3(bodies[i].Copy(),false,1);
   if(f==null)throw new Exception("Body import failed"); f.Name=names[i];
  }
  object[] solids=(object[])part.GetBodies2(0,false);
  if(solids==null || solids.Length!=bodies.Length)throw new Exception("Wrong solid body count");
  for(int i=0;i<solids.Length;i++){
   IBody2 b=(IBody2)solids[i];
   double v=Volume(b);
   b.Name=v<0.0001?"Fluid_Water":"Solid_AlSi10Mg";
   report.AppendLine(name+": "+b.Name+", volume="+(v*1e9).ToString("F6")+" mm^3");
  }
  doc.ForceRebuild3(false);
  doc.ShowNamedView2("*Isometric",7); doc.ViewZoomtofit2();
  Save(doc,Path.Combine(dir,name+".SLDPRT"));
  Save(doc,Path.Combine(dir,name+".x_t"));
  return doc;
 }
 public static string Run(string dir){
  Directory.CreateDirectory(dir);
  foreach(string n in new string[]{"Canopy_Outlet7_CHT","Canopy_Outlet7_Fluid","Canopy_Outlet7_Solid"})
   if(File.Exists(Path.Combine(dir,n+".SLDPRT")))throw new Exception("Existing CAD file, refusing overwrite: "+n);
  ISldWorks app=(ISldWorks)Activator.CreateInstance(Type.GetTypeFromProgID("SldWorks.Application"));
  modeler=(IModeler)app.GetModeler();
  // SI units. Controlled internal manifold enlargement; sharp transition at y=10 mm.
  IBody2 fluid=Cylinder(.125,0,.005,0,1,0,.003,.125);
  double[] diameters={.0031,.0037,.0044,.0049};
  fluid=Op(fluid,Cylinder(.025,.025,.005,1,0,0,diameters[0]/2,.1),15903);
  fluid=Op(fluid,Cylinder(.025,0,.005,0,1,0,.003,.125),15903);
  for(int i=1;i<4;i++)fluid=Op(fluid,Cylinder(.025,.025+i*.1/3,.005,1,0,0,diameters[i]/2,.1),15903);
  // Retain D6 port over y=0..10 mm; enlarge this internal trunk to D7.
  fluid=Op(fluid,Cylinder(0.025,.010,.005,0,1,0,.0035,.115),15903);
  IBody2 block=(IBody2)modeler.CreateBodyFromBox(new double[]{.075,.075,0,0,0,1,.150,.150,.010});
  double vf=Volume(fluid), vb=Volume(block);
  IBody2 inside=Op((IBody2)block.Copy(),(IBody2)fluid.Copy(),15901);
  if(Math.Abs(Volume(inside)-vf)>1e-12)throw new Exception("Fluid extends outside plate");
  IBody2 solid=Op(block,(IBody2)fluid.Copy(),15902);
  double vs=Volume(solid);
  // Mass-property integration has finite accuracy on curved intersections.
  if(Math.Abs(vs+vf-vb)/vb>1e-6)throw new Exception("Volume partition differs by more than one part per million");
  foreach(IBody2 b in new IBody2[]{solid,fluid}) {
   IFaultEntity faults=(IFaultEntity)b.Check3;
   if(faults!=null && faults.Count>0)throw new Exception("Body geometry faults: "+faults.Count);
  }
  report.AppendLine("SolidWorks revision: "+app.RevisionNumber());
  report.AppendLine("One connected fluid body; one connected solid body.");
  report.AppendLine("No geometry faults reported by Check3.");
  report.AppendLine("Fluid containment tolerance: 1e-12 m^3. Volume partition tolerance: 1 ppm of block volume.");
  report.AppendLine("Volume partition difference = "+((vs+vf-vb)*1e9).ToString("F6")+" mm^3 (mass-property integration).");
  report.AppendLine("Full block volume = "+(vb*1e9).ToString("F6")+" mm^3.");
  Document(app,dir,"Canopy_Outlet7_Fluid",new IBody2[]{fluid},new string[]{"Nominal_Channel_Network"});
  Document(app,dir,"Canopy_Outlet7_Solid",new IBody2[]{solid},new string[]{"Nominal_Cooled_Plate"});
  Document(app,dir,"Canopy_Outlet7_CHT",new IBody2[]{solid,fluid},new string[]{"Nominal_Cooled_Plate","Nominal_Channel_Network"});
  File.WriteAllText(Path.Combine(dir,"CAD_Checks.txt"),report.ToString());
  return report.ToString();
 }
}
'@
try { [Outlet7Cad]::Run([System.IO.Path]::GetFullPath($OutputDirectory)) } catch { Write-Output $_.Exception.ToString(); throw }
