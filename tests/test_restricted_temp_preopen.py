"""Exact tempfile opener compatibility, without workbook creation or I/O."""
import importlib.util, os, pathlib, subprocess, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import restricted_recovery_build as driver

class ExactTemporaryPreopenTests(unittest.TestCase):
    def setUp(self):
        self.root=pathlib.Path('/tmp/recovery-synthetic-root')
        self.temp=pathlib.Path('/tmp/recovery-synthetic-worksheet-only')
        self.guard=driver.RestrictedIOGuard(self.root)
        self.guard.configure([self.root/'site/exports/bnu-approved.xlsx'],self.temp)
        self.flags=os.O_RDWR|os.O_CREAT|os.O_TRUNC|getattr(os,'O_CLOEXEC',0)
    def test_only_exact_configured_directory_wplus_preopen(self):
        self.guard('open',(str(self.temp),'w+',self.flags))
        for path,mode,flags in [(self.temp,'w',self.flags),(self.temp,'a+',self.flags),(self.temp,'w+',os.O_RDWR),(self.temp.parent,'w+',self.flags),(self.temp/'unregistered.xml','w+',self.flags)]:
            with self.assertRaises(PermissionError):self.guard('open',(str(path),mode,flags))
    def test_export_temp_preopen_only_registered_suffix_and_exact_parent(self):
        exports=self.root/'site/exports'
        self.guard('open',(str(exports),'w+',self.flags))
        for path in (exports/'unregistered.xlsx.tmp',self.root/'site/people',self.root/'site'):
            with self.assertRaises(PermissionError):self.guard('open',(str(path),'w+',self.flags))
        with self.assertRaises(PermissionError):self.guard('tempfile.mkstemp',(str(exports/'wrong.xml'),))
        with self.assertRaises(PermissionError):self.guard('tempfile.mkstemp',(str(self.root/'site/elsewhere/t.xlsx.tmp'),))
        approved=exports/'random.xlsx.tmp'
        self.guard('tempfile.mkstemp',(str(approved),))
        self.guard('open',(str(approved),'w+',self.flags))

    def test_no_unconfigured_directory_exception(self):
        g=driver.RestrictedIOGuard(self.root)
        with self.assertRaises(PermissionError):g('open',(str(self.temp),'w+',self.flags))
    def test_real_files_still_require_registration_and_exact_rename(self):
        path=self.temp/'openpyxl.synthetic'
        with self.assertRaises(PermissionError):self.guard('open',(str(path),'w+',self.flags))
        self.guard('tempfile.mkstemp',(str(path),))
        self.guard('open',(str(path),'w+',self.flags))
        with self.assertRaises(PermissionError):self.guard('os.rename',(str(path),str(self.root/'site/exports/unlisted.xlsx'),-1,-1))
        with self.assertRaises(PermissionError):self.guard('open',(str(self.root/'site/exports/unlisted.xlsx'),'rb',os.O_RDONLY))
    def test_actual_named_temporary_xml_probe_no_workbook(self):
        script=r'''
import pathlib,sys,tempfile
sys.dont_write_bytecode=True
sys.path.insert(0,sys.argv[1])
from restricted_recovery_build import RestrictedIOGuard
with tempfile.TemporaryDirectory(prefix='recovery-approved-xml-probe-') as outer:
 root=pathlib.Path(outer); temp=root/'worksheet-temp';temp.mkdir();exports=root/'site/exports';exports.mkdir(parents=True)
 guard=RestrictedIOGuard(root);guard.configure([],temp);sys.addaudithook(guard)
 try:
  with tempfile.NamedTemporaryFile(mode='w+',prefix='openpyxl.',dir=temp,delete=False) as f:
   f.write('<worksheet/>');path=pathlib.Path(f.name)
  assert path in guard.temporary and path.parent==temp
  assert path.read_text()=='<worksheet/>'
  path.unlink();assert not list(temp.iterdir())
  with tempfile.NamedTemporaryFile(dir=exports,suffix='.xlsx.tmp',delete=False) as f:
   f.write(b'<xml-probe-not-a-workbook/>');path=pathlib.Path(f.name)
  assert path in guard.temporary and path.parent==exports
  assert path.read_bytes()==b'<xml-probe-not-a-workbook/>'
  path.unlink();assert not list(exports.iterdir())
 finally:guard.enabled=False
print('XML_ONLY_REGISTERED_TEMP_PASS')
'''
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        result=subprocess.run([sys.executable,'-B','-c',script,str(ROOT/'scripts')],capture_output=True,text=True,env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('XML_ONLY_REGISTERED_TEMP_PASS',result.stdout)

if __name__=='__main__':unittest.main()
