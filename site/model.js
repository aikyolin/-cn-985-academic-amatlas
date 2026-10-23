export const CAMPUS_LABELS={harbin:'哈尔滨',weihai:'威海',shenzhen:'深圳',unknown:'校区待核实'};
export const REGION_LABELS={mainland:'中国内地',hmt:'港澳台',overseas:'其他国家或地区',unknown:'未核实',not_recorded:'未记录确证授位'};
export const CONTINENT_LABELS={asia:'亚洲',europe:'欧洲',north_america:'北美洲',south_america:'南美洲',africa:'非洲',oceania:'大洋洲',antarctica:'南极洲',unknown:'未核实',not_recorded:'未记录确证授位'};
export function degreeType(x){const s=String(x||'');if(/博士后|postdoc/i.test(s))return 'postdoc';if(/博士|ph\.?d/i.test(s))return 'doctor';if(/硕士|master/i.test(s))return 'master';if(/本科|学士|bachelor/i.test(s))return 'bachelor';return 'other'}
export const provisionalDegree=e=>String(e.field_status?.degree||'').startsWith('provisional_');
const EVENT_LABELS={education_background:'教育背景（层次与性质未核实）',academic_visit:'学术访问（非学位）',joint_doctoral_training:'博士联合培养（非独立授位）',visiting_postdoctoral_research:'访问博士后研究',professional_research:'职业科研（非学历、非博士后）',postdoctoral_exchange:'博士后交流',study_level_unconfirmed:'学习经历（层次未核实）',visiting_doctoral_student:'博士阶段访问',training:'培训经历',language_study:'语言学习',doctoral_study:'博士阶段学习（授位未核实）',visiting_doctoral_research:'博士阶段访问研究',visiting_research:'访问研究',academic_exchange_or_training:'学术交流或进修',postdoctoral:'博士后研究',postdoctoral_research:'博士后研究',visiting_fellow:'访问研究员',visiting_researcher:'访问研究员',visiting_scholar:'访问学者',visiting_student:'访问学生',visiting_phd_student:'博士阶段访问',visiting_professor:'访问教授',joint_training:'联合培养',visiting_study:'访问学习',overseas_study:'海外学习',professional_training:'专业培训',non_degree_training:'非学位培训',degree_study:'学习经历（学位层次未披露）',study_level_not_disclosed:'学习经历（层次未披露）',study_stage_unspecified:'学习经历（阶段未披露）'};
export const educationStageLabel=e=>String(e.degree||EVENT_LABELS[e.event_kind]||'研究经历')+(provisionalDegree(e)?'（层次暂对应，未核实）':'');
export function stages(p,type){return (p.education||[]).filter(e=>e.event_kind==='degree'&&e.degree_awarded===true&&!provisionalDegree(e)&&degreeType(e.degree)===type)}
// A combined source statement remains one relationship, never one edge per event.
export function mentorEvents(p,m){
 if(Object.hasOwn(m,'education_event_ids')){
  const ids=m.education_event_ids;
  if(!Array.isArray(ids)||!ids.length||ids.some(id=>typeof id!=='string'||!id.trim())||new Set(ids).size!==ids.length)return [];
  if(m.education_event_id&&(ids.length!==1||ids[0]!==m.education_event_id))return [];
  const matches=ids.map(id=>(p.education||[]).filter(e=>e.event_id===id));
  return matches.every(rows=>rows.length===1)?matches.map(rows=>rows[0]):[];
 }
 if(m.education_event_id){const e=(p.education||[]).find(e=>e.event_id===m.education_event_id);return e?[e]:[]}
 const stage=String(m.education_stage||'');if(!stage||/未细分/.test(stage))return [];
 const events=/博士后/.test(stage)?(p.appointments||[]).filter(e=>/博士后/.test(e.title||'')):(p.education||[]).filter(e=>e.degree&&(String(e.degree).includes(stage)||stage.includes(String(e.degree))));
 return events.length===1?events:[];
}
// Legacy single-event callers must not silently select the first combined stage.
// The optional all flag lets the graph retain its existing injected helper contract.
export function mentorEvent(p,m,all=false){const events=mentorEvents(p,m);return all?events:events.length===1?events[0]:{}}
export function professionalGuidanceEvent(p,c){
 if(typeof c.education_event_id!=='string'||!c.education_event_id.trim())return {};
 const events=(p.education||[]).filter(e=>e.event_id===c.education_event_id);
 return events.length===1&&events[0].event_kind==='professional_research'&&events[0].degree_awarded===false?events[0]:{};
}
export function matchEducation(p,type,key,value){if(!value)return true;const rows=stages(p,type);if(value==='not_recorded')return rows.length===0;return rows.some(e=>(e[key]||'unknown')===value)}
export function orgContains(units,ancestor,leaf){const seen=new Set();let id=leaf;while(id&&!seen.has(id)){if(id===ancestor)return true;seen.add(id);const current=units.find(u=>u.id===id),parent=units.find(u=>u.id===current?.parent_id);if(current?.school_id&&parent?.school_id&&current.school_id!==parent.school_id)return false;id=current?.parent_id}return false}
export function matches(p,f,orgUnits=[]){if(f.school&&p.school_id!==f.school)return false;if(f.campus&&!(p.campus_ids||[]).includes(f.campus))return false;if(f.org){const org=orgUnits.find(o=>o.id===f.org);if(!org||(org.school_id&&org.school_id!==p.school_id)||!orgContains(orgUnits,f.org,p.department_id))return false;}if(f.q){const hay=[p.name,p.department,p.research_interests,...(p.education||[]).map(e=>e.institution)].join(' ').toLowerCase();if(!hay.includes(f.q.toLowerCase().trim()))return false}return matchEducation(p,'bachelor','institution_985',f.ug)&&matchStageFilters(p,'master',f.master,f.master_continent)&&matchStageFilters(p,'doctor',f.doctor,f.continent)}
export function safeUrl(v){try{const u=new URL(v);return ['https:','http:'].includes(u.protocol)?u.href:''}catch{return ''}}
export function escapeHtml(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

export function navigableProfileUrl(v){const safe=safeUrl(v);if(!safe)return "";const u=new URL(safe);return /\/_cms\/|articleEdit|https?:/i.test(u.pathname)||u.searchParams.get("act")==="edit"?"":safe}

export function matchStageFilters(p,type,region,continent){if(!region&&!continent)return true;const rows=stages(p,type);if(region==='not_recorded'||continent==='not_recorded')return rows.length===0&&(!region||region==='not_recorded')&&(!continent||continent==='not_recorded');return rows.some(e=>(!region||(e.region||'unknown')===region)&&(!continent||(e.continent_code||'unknown')===continent))}

export function collaboratorEvent(p,c){if(c.education_event_id)return (p.education||[]).find(e=>e.event_id===c.education_event_id)||{};if(c.appointment_event_id)return (p.appointments||[]).find(e=>e.event_id===c.appointment_event_id)||{};return {}}

// Profile navigation needs a verified active relation and a real stored person.
export function mentorProfileRoute(mentor,people=[]){const id=mentor?.person_id;if(mentor?.employment_status!=='active_officially_listed'||mentor.quick_link_eligible===false||typeof id!=='string'||!id.trim()||/^(unknown|null|undefined)$/i.test(id.trim())||!Array.isArray(people)||!people.some(p=>p?.person_id===id))return '';try{return '#/person/'+encodeURIComponent(id)}catch{return ''}}

// An explicit navigation veto overrides active employment; absent flags preserve reviewed legacy links.
export function mentorOfficialUrl(mentor){return mentor?.employment_status==='active_officially_listed'&&mentor.quick_link_eligible!==false&&mentor.navigation_verified!==false?safeUrl(mentor.official_url):''}
export function mentorNavigationNotice(mentor){if(mentor?.employment_status!=='active_officially_listed'||mentorOfficialUrl(mentor))return '';const reason=mentor.profile_navigation_unavailable_reason;return '任职已核实；'+((typeof reason==='string'?reason.trim():'')||'导师主页访问未核实，暂不提供快捷链接。')}

export function officialProfileUrl(p){return p?.official_profile_availability==='unavailable'||p?.official_profile_navigation_eligible===false?'':navigableProfileUrl(p?.official_url)}

export function versionedPath(path,buildId){return String(path)+(buildId?(String(path).includes('?')?'&':'?')+'v='+encodeURIComponent(buildId):'')}
export function sameBuild(atlas,rosters){return typeof atlas?.build_id==='string'&&atlas.build_id.length>0&&atlas.build_id===rosters?.build_id}

// School and campus scope is explicit. Empty campus associations never imply HIT.
export const institutions=db=>db.institutions||(db.institution?[db.institution]:[]);
export const schoolName=(db,id)=>institutions(db).find(s=>s.id===id)?.official_name||id||'学校未标注';
export const schoolCampuses=(db,id='')=>(db.campuses||[]).filter(c=>!id||c.school_id===id);
export const schoolUnits=(db,id='',campus='')=>(db.org_units||[]).filter(o=>(!id||o.school_id===id)&&(!campus||(o.campus_ids||[]).includes(campus)));
export function campusId(record){const id=record?.campus_id||'';return record?.school_id==='hit'&&['hit-harbin','hit-weihai','hit-shenzhen'].includes(id)?id.slice(4):id}
export function campusLabel(db,id,school=''){return (db.campuses||[]).find(c=>c.id===id&&(!school||c.school_id===school))?.name||'校区未标注／待核实'}
export function schoolStats(db,id){const inSchool=rows=>(rows||[]).filter(r=>r.school_id===id);const people=inSchool(db.people),pending=inSchool(db.pending_people),units=inSchool(db.org_units),rosters=inSchool(db.rosters?.entries);return {people:people.length,pending:pending.length,units:units.length,rosters:rosters.length,published:people.length>0,hasData:Boolean(people.length||pending.length||units.length||rosters.length),status:people.length?'部分收录':pending.length||units.length||rosters.length?'仅目录／资料待核':'待收录'}}
export function normalizeSchoolFilters(db,f){const next={...f};if(next.campus&&!schoolCampuses(db,next.school).some(c=>c.id===next.campus))next.campus='';if(next.org&&!schoolUnits(db,next.school,next.campus).some(o=>o.id===next.org))next.org='';return next}
export function routeSchool(db,type,id,querySchool=''){if(type==='school')return id;if(type==='org')return db.org_units.find(o=>o.id===id)?.school_id||'';if(type==='person')return [...db.people,...(db.pending_people||[])].find(p=>p.person_id===id)?.school_id||'';if(type==='roster')return db.rosters?.entries.find(e=>e.id===id)?.school_id||'';if(type==='campus')return id==='all'?(querySchool||'hit'):(db.campuses.find(c=>c.id===id)?.school_id||'');return querySchool}
export function rosterMatches(db,e,school='',query=''){const q=String(query).trim().toLowerCase();return (!school||e.school_id===school)&&[e.name,e.category,e.listed_role,schoolName(db,e.school_id),db.org_units.find(o=>o.id===e.organization_id&&o.school_id===e.school_id)?.name,campusLabel(db,campusId(e),e.school_id)].join(' ').toLowerCase().includes(q)}
