"""Explicit school views for immutable historical HIT regression expectations.

These views never rewrite a person's evidence. Full-dataset validation remains in
separate tests, so adding another school cannot bypass canonical validation.
"""
import copy

ATLAS_ROWS=('campuses','org_units','people','pending_people','profile_batches','exports')

def hit_atlas(atlas):
    result=copy.deepcopy(atlas)
    for key in ATLAS_ROWS:
        if key in result: result[key]=[r for r in result[key] if r.get('school_id')=='hit']
    if 'institutions' in result: result['institutions']=[s for s in result['institutions'] if s['id']=='hit']
    return result

def hit_rosters(rosters):
    result=copy.deepcopy(rosters)
    for key,rows in result.items():
        if isinstance(rows,list) and rows and isinstance(rows[0],dict):
            result[key]=[r for r in rows if r.get('school_id')=='hit']
    entries=result['entries'];coverage=result['coverage']
    if 'totals' in result:
        # Derive only scoped counters from preserved rows, never substitute the
        # expected historical constants. Full global counters are checked apart.
        raw=len(result['source_observations']) if 'source_observations' in result else sum(c['visible_name_count'] for c in coverage)
        result['totals'].update(
            record_count=len(entries),roster_records=len(entries),
            raw_observation_count=raw,raw_source_observations=raw,
            entries_with_profile_link=sum(bool(e['official_profile_url']) for e in entries),
            entries_without_profile_link=sum(not e['official_profile_url'] for e in entries),
            organization_count=len({e['organization_id'] for e in entries}),
            category_count=len({(c['organization_id'],c['category']) for c in coverage}),
            coverage_unit_count=len(coverage),
            dedup_candidate_groups=len(result.get('dedup_candidates',[])),
            source_record_grouping_reduction=raw-len(entries))
    return result

def hit_export_rows(rows,organization_ids):
    """Filter an exported roster by explicit school or verified HIT unit IDs."""
    rows=list(rows);header=rows[0]
    if '所属学校ID' in header:
        index=header.index('所属学校ID');selected=[r for r in rows[1:] if r[index]=='hit']
    else:
        index=header.index('组织ID');selected=[r for r in rows[1:] if r[index] in organization_ids]
    return [header,*selected]
