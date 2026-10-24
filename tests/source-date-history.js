// One pinned Python transition engine supplies identical exact historical bytes.
// Always validate the actual requested test root; never substitute local clean bytes.
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const testedRoot=()=>process.env.ACADEMIC_ATLAS_TEST_ROOT||ROOT;
export function historicalBytes(rel,root=testedRoot()){
  if(typeof rel!=='string'||!rel||rel.includes('\\')||path.posix.normalize(rel)!==rel||rel.startsWith('/')||rel.split('/').some(x=>x==='.'||x==='..'))throw new TypeError('Invalid historical path');
  return execFileSync('python',['-B',path.join(ROOT,'tests/source_date_history.py'),'read',rel,path.resolve(root)],{cwd:ROOT,maxBuffer:32*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'},stdio:['pipe','pipe','pipe']});
}
export function validateCurrentTree(root=testedRoot()){
  return JSON.parse(execFileSync('python',['-B',path.join(ROOT,'tests/source_date_history.py'),'validate',path.resolve(root)],{cwd:ROOT,encoding:'utf8',maxBuffer:2*1024*1024,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'},stdio:['pipe','pipe','pipe']}));
}
export async function withHistoricalAppRoot(root,callback){
  const directory=fs.mkdtempSync(path.join(os.tmpdir(),'atlas-history-app-'));
  try{
    for(const rel of ['package.json','site/app.js','site/model.js','site/rosters.js','site/universities.js']){
      const target=path.join(directory,rel);fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,historicalBytes(rel,root));
    }
    return await callback(directory);
  }finally{fs.rmSync(directory,{recursive:true,force:true});}
}
