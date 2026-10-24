# 参与贡献

欢迎用自己的 AI 辅助补充资料、纠错、改进界面、测试与文档。请让提交者实际核对来源与差异，再提交一个小而可审核的 PR。AI 生成的内容不因写得完整就成为证据。

- [项目仓库](https://github.com/aikyolin/-cn-985-academic-amatlas)
- [浏览网站](https://aikyolin.github.io/-cn-985-academic-amatlas/)
- [可直接复制给 AI 的中文提示词](docs/ai-contributor-prompt.md)
- [贡献者记录](CONTRIBUTORS.md)
- [公开来源元数据规范](docs/public-source-metadata.md)

## 先选小范围，再开始

目标是覆盖中国原 39 所 985 高校。新资料优先拓展尚未建立人物档案的学校，先为每校做 3–5 位有直接证据的教师样本，再逐步深入院系；不要为了凑数降低证据标准。现有学校的纠错、来源补强和功能修复同样欢迎。

1. 读取最新默认分支、[当前覆盖](progress/current-coverage.md)、[任务队列](progress/work-queue.json)、[数据政策](docs/data-policy.md)、[多校约定](docs/multischool-data-contract.md)及[接续规则](docs/continuation.md)。实际字段以当前 `schema/`、构建程序和测试共同为准。
2. 搜索 [开放 PR](https://github.com/aikyolin/-cn-985-academic-amatlas/pulls) 和 [Issues](https://github.com/aikyolin/-cn-985-academic-amatlas/issues)，检查同校、同院系、同名人物与同一问题是否已经有人处理。已关闭的相关 PR 也可能有结论。
3. 用已有 issue 的一条认领留言，或一个范围明确的新 issue，说明拟处理学校、院系、人数及目标。由本人操作，或交给本人明确授权的 AI 操作。遇到已有认领先协调，不覆盖他人成果。没有发布权限时先准备本地方案，不声称已经认领。
4. Fork 仓库，在自己的 fork 建独立分支，例如 `contrib/<school-id>-first-sample`。尽早开 Draft PR，写清范围和基准提交，避免长期隐形并行。不要直接推送上游 `main`，不要强推覆盖他人分支。
5. 一个 PR 尽量只处理一个学校/院系的小批资料，或一个功能问题。未经协调不要重写全库、批量格式化、更新无关依赖、改工作流或替别人标记任务完成。共享进度队列由维护者合并时协调更新。

## 资料与证据

### 学校、院系和身份

- 主数据在 `data/atlas.json`，独立名录在 `data/rosters.json`。`site/atlas.json`、`site/rosters.json` 和导出文件是构建产物，不能只改产物而不改源数据。
- 学校使用 `institutions: {id, official_name, official_url}`；院系使用 `org_units: {id, school_id, name, type, parent_id, campus_ids, source_url}`，保留真实上下级，不把学部、学院、系、研究所全改成学院。
- 人物必须有全球唯一 `person_id`、明确 `school_id`、同校的 `department_id` 及显式 `campus_ids`。未知校区用 `[]`，不默认哈尔滨工业大学，也不表示该校没有校区。新校区 ID 使用 `<school_id>-...`；保留已有 HIT 兼容 ID。学校、校区、院系 ID 只用英文字母、数字、下划线和连字符。
- 姓名相同、拼音相近、共用网址均不能自动合并身份。只核到名录、身份或正文仍不足者，依现有约定留在名录或 `pending_people`，并引用真实同校 `roster_entry_id`。不得给待核记录制造学历、导师或论文。

### 学历与三态未知

每条 `education` 至少遵循当前 schema：`degree`、`institution`、`source_url`、`institution_985`、`region`、`continent_code`、`event_kind`、`degree_awarded`。同时沿用现有字段来源和事件 ID 机制，不把一个字段的来源套给全部字段。

- `degree_awarded: true` 仅用于有直接授位依据且 `event_kind: "degree"` 的记录；`false` 用于明确非授位事件；`null` 表示未核实授位。不能把未查到学位写成没有学位，也不能由学习区间、毕业年份、论文提交或答辩日期自动确认授位。
- `institution_985` 为 `yes`、`no`、`unknown`，指历史 39 校分类，不代表就读当年已是 985。未知不归为非 985。
- `region` 为 `mainland`、`hmt`、`overseas`、`unknown`；洲使用现有 `continent_code`。地域表示对应院校/授位经历的地理分类，不推断国籍或每段学习实际所在地。
- 访问、联合培养、博士后、进修和工作经历不得混成获授学位。联合培养不能改写授位院校；硕博连读或直博不能凭路径补一个硕士学位。
- 保留未知日期、未披露字段和互相冲突的来源，在 `unknowns`、`note` 及适用的字段状态中说明；不为通过测试或填满卡片而猜测。

### 导师、合作与项目指导

- 导师关系需要官方个人页、原始学位论文/机构库等直接说明。区分本科、硕士、博士、共同/副导师、联合培养、访问和博士后指导，保留原文角色，不把 Associate Advisor、项目 Advisor 一律改为博士导师。
- 已确认关系才放 `mentors`。`education_event_id` 必须指向该人物真实存在且阶段匹配的 `education[].event_id`；阶段不清时不要强行绑定。
- 委员会成员放 `committee_members`；科研合作者按约定放 `research_collaborators`，不进入师承图。委员会、合著、通讯作者、同实验室、致谢或二手转载都不能单独证明师承。
- 竞赛/课题/项目指导放 `project_guidance`，`include_in_mentorship_graph: false`、`include_in_verified_mentor_count: false`、`education_event_id: null`，不充作学位导师。
- 导师简介、关系事实和当前任职分别取证。`active_officially_listed` 必须有直接的现职证据及 `profile_source_url`；有主页不等于在职。来源冲突、荣休、退休或任职未核实时不得启用“在职导师”快捷导航。

### 来源闭合与成果

- 优先学校/院系/教师官方页、原始论文机构库、学会和出版社元数据。搜索摘要、转载及 AI 回答只作线索；未读到原文就写明核验层级，不声称“已读官网正文”。
- 每项学历、任职、导师/项目指导和成果有可追溯 `source_url`。被引用的 `source_id`、`profile_source_id`、`field_provenance` 等 ID 必须在该人物 `sources` 中存在；每个来源记录真实 URL、`evidence_status`、实际 `retrieved_at`。记录可复核的位置或简短事实摘要，勿复制长文。
- 原始来源之间冲突时同时保留，说明未决字段。打不开或受限的来源记录原因，不换身份、代理或其他路径绕过拒绝。
- 论文保留可核验的题名、年份、类型、来源及作者归属依据；优先 DOI/出版社/机构库链接。仅查到教师书目就明确为书目，不能标为已读全文，也不能由同名作者批量归属成果。不能为凑论文数猜 DOI。

## 隐私、版权与访问边界

只提交公开职业学术事实及必要链接。不要提交出生日期、电话、邮箱、住址、证件、家庭信息、学生隐私或私人聊天，即便原页面夹带了这些信息，也应在本项目中排除。不要上传原始网页缓存、完整简历、长段原文、照片、论文全文、课件、答案或其他无权再分发的材料。少量必要证据摘录也应尽量短并标明出处。

发现隐私、凭据或授权争议时，停止相关提交，私下告知维护者；不要在公开 issue/PR 重贴敏感内容。不要绕过登录、验证码、访问限制或浏览器安全警告。

本仓库的许可证尚待所有者选择。公开可见不等于任意复用；本指南不新增许可证、不代表第三方授权、不要求转让版权，也不构成 CLA。不要替所有者添加或变更许可证、凭据、仓库权限、密钥、分支保护、自动合并或部署配置。遇到许可不明的代码/材料先提出问题，不照搬。

## 本地检查

需要 Python 3.10+、Node.js 20+。在自己的工作副本根目录执行：

```sh
python -m pip install -r requirements-dev.txt
python scripts/build.py
python scripts/public_metadata.py --phase final
npm test
python -m unittest discover -s tests -v
python scripts/validate_queue.py progress/work-queue.json --check-artifacts
git diff --check
```

`requirements-dev.txt` 已包含运行依赖；项目没有 `npm run build`，`npm test` 运行 Node 内置测试。完整构建命令 `python scripts/build.py` 会校验并生成网站 JSON/CSV 和院系 XLSX。调试时可用 `python scripts/build.py --data-only`，但它不会更新 XLSX，不能作为涉及数据/导出的最终同步替代。提交前检查所有差异，只保留本 PR 对应的源数据、必要测试与派生产物，避免无关工作簿重写。

查看网页：

```sh
python -m http.server 8000 --directory site
```

打开 `http://localhost:8000/`，核对学校/院系、人物页、师承图、筛选与相关导出；UI 改动还需检查窄屏。涉及 JSON 结构时，对照 schema 与现有回归测试补充测试，不通过删断言、改伪造人数或放宽证据校验来让测试变绿。合成资料仅留在 `tests/fixtures/`。

纯文档 PR 可注明未运行数据构建及原因，但仍应检查链接和 `git diff --check`。其他未运行、失败或受环境限制的检查，必须逐项如实列出；“AI 说没问题”不是测试结果。

## 提交与审核

使用 [PR 模板](.github/pull_request_template.md)，写明范围、来源、未知项、实际运行的命令和结果，以及 AI 辅助的部分与本人复核范围。未检查完成时保持 Draft；准备就绪后由贡献者标记 Ready for review。

维护者会逐 PR 核对来源、身份与字段语义、代码差异、隐私/许可风险和相关测试。CI 通过不代表事实正确，也不保证合并。PR 有新提交后，之前的审核不自动覆盖新 head；合并前核对被审的准确 head 与上游最新状态，必要时重新测试。草稿 PR、证据未闭合或有未决风险的 PR 不合并。涉及争议、隐私、许可、安全设置或大范围破坏性变更，交由仓库所有者确认。

贡献者及其 AI 不应合并自己的 PR、开启自动合并、直接部署或修改权限。审核通过的贡献通过正常维护流程合并；不承诺全天候响应、固定审核时限或机器人自动验真。上线以实际部署成功为准。

## 如何获得署名

合并后可按 [CONTRIBUTORS.md](CONTRIBUTORS.md) 的规则记录公开 GitHub 身份、贡献类型和已合并 PR 链接。资料核验、纠错、代码、测试、文档、可访问性都值得记录，不按人数、提交数或行数排名。AI 工具可在 PR 中披露，不作为独立的人类贡献者添加。
