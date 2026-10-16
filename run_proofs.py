"""Run all bundled exact mathematical check suites without touching benchmark datasets."""
from pathlib import Path
import subprocess,sys,tempfile,shutil,json,time
ROOT=Path(__file__).resolve().parent
SCRIPTS=('verify_extension_v02.py','verify_v03.py','verify_joint_pencils_v04.py','verify_balanced_transfer_v05.py')
def main():
    out=ROOT/'outputs';out.mkdir(exist_ok=True)
    report={'scripts':{},'status':'FAILED'}
    with tempfile.TemporaryDirectory(prefix='proof_verification_') as tmp:
        for source in sorted((ROOT/'verification').glob('*.py')):shutil.copy2(source,Path(tmp)/source.name)
        for name in SCRIPTS:
            t=time.monotonic()
            p=subprocess.run([sys.executable,str(Path(tmp)/name)],cwd=tmp,text=True,capture_output=True,timeout=120)
            (out/(name+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf8')
            report['scripts'][name]={'exit_code':p.returncode,'duration_sec':round(time.monotonic()-t,3)}
            print(name,'PASS' if p.returncode==0 else 'FAILED')
            if p.returncode:print(p.stdout[-1500:]);print(p.stderr[-1500:]);break
        else:report['status']='PASSED'
    (out/'proof_verification_status.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    if report['status']!='PASSED':raise SystemExit(1)
    print('All four independent mathematical verification suites passed.')
if __name__=='__main__':main()
