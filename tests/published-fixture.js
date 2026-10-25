// Explicit input for historical release assertions, never a live-test override.
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const TESTS=path.dirname(fileURLToPath(import.meta.url));
let root;
export function publishedRoot(){
  if(root)return root;
  root=fs.mkdtempSync(path.join(os.tmpdir(),'atlas-published-js-'));
  try{
    execFileSync('python',['-B','-c','import shutil,sys; from published_fixture import published_root; shutil.copytree(published_root(),sys.argv[1],dirs_exist_ok=True)',root],{cwd:TESTS,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  }catch(error){fs.rmSync(root,{recursive:true,force:true});root=undefined;throw error;}
  process.once('exit',()=>fs.rmSync(root,{recursive:true,force:true}));
  return root;
}
