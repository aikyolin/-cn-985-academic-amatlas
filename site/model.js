export const CAMPUS_LABELS={harbin:'哈尔滨',weihai:'威海',shenzhen:'深圳',unknown:'校区待核实'};
export const REGION_LABELS={mainland:'中国内地',hmt:'港澳台',overseas:'其他国家或地区',unknown:'未核实',not_recorded:'未记录确证授位'};
export const CONTINENT_LABELS={asia:'亚洲',europe:'欧洲',north_america:'北美洲',south_america:'南美洲',africa:'非洲',oceania:'大洋洲',antarctica:'南极洲',unknown:'未核实',not_recorded:'未记录确证授位'};
export function degreeType(x){const s=String(x||'');if(/博士后|postdoc/i.test(s))return 'postdoc';if(/博士|ph\.?d/i.test(s))return 'doctor';if(/硕士|master/i.test(s))return 'master';if(/本科|学士|bachelor/i.test(s))return 'bachelor';return 'other'}
export const provisionalDegree=e=>String(e.field_status?.degree||'').startsWith('provisional_');
const EVENT_LABELS={visiting_doctoral_research:'博士阶段访问研究',visiting_research:'访问研究',academic_exchange_or_training:'学术交流或进修',postdoctoral:'博士后研究',postdoctoral_research:'博士后研究',visiting_fellow:'访问研究员',visiting_researcher:'访问研究员',visiting_scholar:'访问学者',visiting_student:'访问学生',visiting_phd_student:'博士阶段访问',visiting_professor:'访问教授',joint_training:'联合培养',visiting_study:'访问学习',overseas_study:'海外学习',professional_training:'专业培训',non_degree_training:'非学位培训',degree_study:'学习经历（学位层次未披露）',study_level_not_disclosed:'学习经历（层次未披露）',study_stage_unspecified:'学习经历（阶段未披露）'};
export const educationStageLabel=e=>String(e.degree||EVENT_LABELS[e.event_kind]||'研究经历')+(provisionalDegree(e)?'（层次暂对应，未核实）':'');
export function stages(p,type){return (p.education||[]).filter(e=>e.event_kind==='degree'&&e.degree_awarded===true&&!provisionalDegree(e)&&degreeType(e.degree)===type)}
export function mentorEvent(p,m){if(m.education_event_id)return (p.education||[]).find(e=>e.event_id===m.education_event_id)||{};const stage=String(m.education_stage||'');if(!stage||/未细分/.test(stage))return {};const events=/博士后/.test(stage)?(p.appointments||[]).filter(e=>/博士后/.test(e.title||'')):(p.education||[]).filter(e=>e.degree&&(String(e.degree).includes(stage)||stage.includes(String(e.degree))));return events.length===1?events[0]:{}}
export function matchEducation(p,type,key,value){if(!value)return true;const rows=stages(p,type);if(value==='not_recorded')return rows.length===0;return rows.some(e=>(e[key]||'unknown')===value)}
export function orgContains(units,ancestor,leaf){const seen=new Set();let id=leaf;while(id&&!seen.has(id)){if(id===ancestor)return true;seen.add(id);id=units.find(u=>u.id===id)?.parent_id}return false}
export function matches(p,f,orgUnits=[]){if(f.campus&&!p.campus_ids.includes(f.campus))return false;if(f.org&&!orgContains(orgUnits,f.org,p.department_id))return false;if(f.q){const hay=[p.name,p.department,p.research_interests,...(p.education||[]).map(e=>e.institution)].join(' ').toLowerCase();if(!hay.includes(f.q.toLowerCase().trim()))return false}return matchEducation(p,'bachelor','institution_985',f.ug)&&matchStageFilters(p,'master',f.master,f.master_continent)&&matchStageFilters(p,'doctor',f.doctor,f.continent)}
export function safeUrl(v){try{const u=new URL(v);return ['https:','http:'].includes(u.protocol)?u.href:''}catch{return ''}}
export function escapeHtml(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}

export function navigableProfileUrl(v){const safe=safeUrl(v);if(!safe)return "";const u=new URL(safe);return /\/_cms\/|articleEdit|https?:/i.test(u.pathname)||u.searchParams.get("act")==="edit"?"":safe}

export function matchStageFilters(p,type,region,continent){if(!region&&!continent)return true;const rows=stages(p,type);if(region==='not_recorded'||continent==='not_recorded')return rows.length===0&&(!region||region==='not_recorded')&&(!continent||continent==='not_recorded');return rows.some(e=>(!region||(e.region||'unknown')===region)&&(!continent||(e.continent_code||'unknown')===continent))}

export function collaboratorEvent(p,c){if(c.education_event_id)return (p.education||[]).find(e=>e.event_id===c.education_event_id)||{};if(c.appointment_event_id)return (p.appointments||[]).find(e=>e.event_id===c.appointment_event_id)||{};return {}}

// Profile navigation needs a verified active relation and a real stored person.
export function mentorProfileRoute(mentor,people=[]){const id=mentor?.person_id;if(mentor?.employment_status!=='active_officially_listed'||mentor.quick_link_eligible===false||typeof id!=='string'||!id.trim()||/^(unknown|null|undefined)$/i.test(id.trim())||!Array.isArray(people)||!people.some(p=>p?.person_id===id))return '';try{return '#/person/'+encodeURIComponent(id)}catch{return ''}}
