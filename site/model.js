export const CAMPUS_LABELS={harbin:'哈尔滨',weihai:'威海',shenzhen:'深圳',unknown:'校区待核实'};
export const REGION_LABELS={mainland:'中国内地',hmt:'港澳台',overseas:'其他国家或地区',unknown:'未核实',not_recorded:'未收录该阶段'};
export const CONTINENT_LABELS={asia:'亚洲',europe:'欧洲',north_america:'北美洲',south_america:'南美洲',africa:'非洲',oceania:'大洋洲',antarctica:'南极洲',unknown:'未核实',not_recorded:'未收录该阶段'};
export function degreeType(x){const s=String(x||'');if(/博士后|postdoc/i.test(s))return 'postdoc';if(/博士|ph\.?d/i.test(s))return 'doctor';if(/硕士|master/i.test(s))return 'master';if(/本科|学士|bachelor/i.test(s))return 'bachelor';return 'other'}
export function stages(p,type){return (p.education||[]).filter(e=>degreeType(e.degree)===type)}
export function matchEducation(p,type,key,value){if(!value)return true;const rows=stages(p,type);if(value==='not_recorded')return rows.length===0;return rows.some(e=>(e[key]||'unknown')===value)}
export function orgContains(units,ancestor,leaf){const seen=new Set();let id=leaf;while(id&&!seen.has(id)){if(id===ancestor)return true;seen.add(id);id=units.find(u=>u.id===id)?.parent_id}return false}
export function matches(p,f,orgUnits=[]){if(f.campus&&!p.campus_ids.includes(f.campus))return false;if(f.org&&!orgContains(orgUnits,f.org,p.department_id))return false;if(f.q){const hay=[p.name,p.department,p.research_interests,...(p.education||[]).map(e=>e.institution)].join(' ').toLowerCase();if(!hay.includes(f.q.toLowerCase().trim()))return false}return matchEducation(p,'bachelor','institution_985',f.ug)&&matchEducation(p,'master','region',f.master)&&matchEducation(p,'doctor','region',f.doctor)&&matchEducation(p,'doctor','continent_code',f.continent)&&matchEducation(p,'master','continent_code',f.master_continent)}
export function safeUrl(v){try{const u=new URL(v);return ['https:','http:'].includes(u.protocol)?u.href:''}catch{return ''}}
export function escapeHtml(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
