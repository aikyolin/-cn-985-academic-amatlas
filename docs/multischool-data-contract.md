# Multi-school data contract

The historical 39-school navigation registry is separate from published academic data. A school is “部分收录” only when it has real published person profiles (including explicitly labeled partial professional profiles); directory-only or pending-only content is “仅目录／资料待核”. Registry presence alone means “待收录”. No school is marked complete by this implementation.

## Canonical input

- `institutions`: array of `{id, official_name, official_url}`. An optional school-specific `scope_note` can explain sampled coverage. Keep the old singular `institution` only as a compatibility alias for the original HIT data, not as a default owner for other records.
- `campuses`: optional-per-school records `{id, school_id, name}` with official evidence fields where supplied. School records need not have campus records. New campus IDs must start with `<school_id>-`. The existing HIT IDs `harbin`, `weihai`, `shenzhen` remain valid for old deep links.
- `org_units`: `{id, school_id, name, type, parent_id, campus_ids, source_url}`. IDs are globally unique. `parent_id` is null, the same institution ID, a same-school parent unit, or a same-school campus. Existing HIT parent aliases `hit-harbin`, `hit-weihai`, `hit-shenzhen` remain supported. Do not flatten real nested faculties, schools, departments, or institutes.
- Every published person and pending person has an explicit `school_id`, globally unique `person_id`, correct `department_id`, and explicit `campus_ids`. An empty `campus_ids` means campus attribution is not separately recorded; it neither implies HIT nor asserts that the school has no campuses.
- Published profiles continue using the existing evidence, event, mentor, appointment, publication, source, and unknown-field contract. This adaptation does not infer degrees, current employment, mentors, or identities. A non-award or unknown award must remain such.
- Pending people remain outside published profiles and refer to a real same-school `roster_entry_id`. No detailed publications or mentor events are manufactured to fill a pending record.
- Normalized roster entries, source observation wrappers, summary rows, coverage rows, and single-school batches carry `school_id`. Preserve original nested `source_payload` and all evidence as-is. New roster records may have `campus_id: null`; only historical HIT roster aliases are normalized to the three old campus IDs.
- School, campus, and organization IDs use only ASCII letters, digits, `_`, and `-`. Names are display data, never export paths. Cross-school campus, parent, department, pending-roster, verified-profile, summary, batch, and coverage references are rejected.

A partial professional profile may use `profile_status: partial_professional_source_checked` and an explicit `profile_coverage_label`. The person page displays this label; cards/counts say “已建人物档案” or “人物资料”, not complete biographies.

## Exports and build

Use `python scripts/build.py --data-only` to validate and regenerate JSON/CSV snapshots without writing XLSX files. This creates school-aware departmental manifest rows and a common `build_id` for the atlas and roster snapshots.

For external workbook generation, call:

`department_tables(people, d['updated_at'], d['institutions'])`

It returns the existing five worksheets and appends `所属学校ID` / `所属学校` to every worksheet. It rejects mixed-school inputs. The optional third argument is backward compatible; when absent, the actual school ID is displayed rather than guessing a school name or reading another directory's files. Each department ID remains a globally unique filename.

`roster_tables(rosters, atlas)` keeps its existing signature and appends school identification to the main roster sheet. The roster page's downloads remain explicitly labeled as whole-library exports, even when the on-screen rows are school-filtered.

## Routes and compatibility

- School: `#/school/<school_id>`
- Search: `#/people?school=<school_id>`; campus/org filters can be combined within that school.
- Independent roster: `#/rosters?school=<school_id>`
- Legacy `#/campus/harbin`, `#/org/<id>`, and `#/person/<id>` resolve ownership from the referenced stored entity. Legacy `#/campus/all` means HIT only; it does not affect schools without campus data.
- A school change clears incompatible campus and department filters. Profiles and roster details derive their breadcrumbs from their own `school_id`, not from a prior route.

Synthetic tests live only under `tests/fixtures/`. They are not published data and must never be copied into `data/` or `site/`.
