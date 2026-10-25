# 学术经纬 · 中国985高校学术图谱

面向中国原39所985高校的教师学术经历与师承资料项目，提供学校院系总览、个人档案、分阶段师承关系图、学历地域筛选、论文链接与院系 Excel 导出。

[浏览网站](https://aikyolin.github.io/-cn-985-academic-amatlas/) · [当前覆盖与核验进度](progress/current-coverage.md) · [数据政策](docs/data-policy.md) · [资料补充与纠错讨论](https://github.com/aikyolin/-cn-985-academic-amatlas/discussions)

## 一起贡献

欢迎使用自己的 AI 辅助核验、补充资料、纠错或改进代码。先查看已有任务，按一个小范围提交 Draft PR；证据、测试和风险审核通过后再合并。

[贡献指南](CONTRIBUTING.md) · [复制给 AI 的中文提示词](docs/ai-contributor-prompt.md) · [贡献者](CONTRIBUTORS.md) · [开放 PR](https://github.com/aikyolin/-cn-985-academic-amatlas/pulls) · [Issues](https://github.com/aikyolin/-cn-985-academic-amatlas/issues)

## 项目范围

以公开、可追溯的学术资料为依据，按学校和院系逐批整理。全国范围是项目目标，不代表39所高校已全部收录；目前的实际覆盖、资料缺项与来源冲突均在进度说明中列示。项目不是教师评价或能力排行榜。

个人主页与师承关系分为独立模块。关系图按学习和研究阶段呈现导师及简介；明确在职且身份已匹配者提供导航，状态不明者不推断。来源不充分的学历、任职与关系保留“未核实”，不自动补全。

## 本地运行

需要 Python 3.10+ 和 openpyxl。开发测试另需 Node.js 20+。

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8000 --directory site
```

浏览器访问 http://localhost:8000/。不需要账户、后端或 API Key。请勿直接双击 HTML，因为数据通过 HTTP 加载。

```sh
npm test
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## 模块

- `data/atlas.json`：人物资料的数据源，公开学术事实及来源、冲突、缺项。
- `data/rosters.json`：独立待核对名录数据源，含分类覆盖和冲突；不与人物档案自动合并。
- `scripts/build_rosters.py`：生成独立名录快照与Excel/CSV，标识消歧候选而非合并人物。
- `site/`：静态 UI；个人主页和师承关系为独立路由；手机布局；可组合筛选；CSV、SVG 和 Excel 下载。
- `scripts/build.py`：校验后生成网站数据快照与院系 Excel。
- `schema/atlas.schema.json`：核心结构定义；构建另做学校归属、引用、证据和循环关系检查。
- `docs/multischool-data-contract.md`：多校数据接入、校区可选、学校范围与导出约定。
- `tests/`：筛选语义、安全转义、源数据和工作簿校验。
- `docs/`：数据政策与架构说明。

## 口径

985 是按教育部历史39校名单归类，不表示就读当年已是985。中国内地、港澳台、其他国家或地区分别筛选；洲是另一独立字段。学历筛选仅统计 event_kind=degree 且 degree_awarded=true 的确证授位。博士学习、访问、联合培养及未知授位不计确证毕业。硕博连读按确证博士授位归类，不自动补硕士。联合培养不改写学位授予院校。未收录阶段不等于没有该学位。同一学历阶段的地域与洲条件必须命中同一条确证授位记录，不将两条经历拼成一次匹配。

导师在职快捷导航仅对有直接任职来源且未发现冲突者提供。其他导师只显示简介与证据，绝不由“有主页”推断在职。委员会成员不计入师承边。官方页面之间存在的月份、毕业/授位时间与职称冲突保留原说明。

## 尚未完成

全国高校教师收录、完整教育史和成果清单、所有院系校区归属核实、自动资料更新尚未完成；资料补充与纠错通过 Issues 和 PR 提交。当前不含定时爬虫，不会绕过登录、验证码或访问限制。经核验的仓库更新通过 GitHub Pages 同步展示；在线版本以成功部署为准。

## 权利说明

许可证待仓库所有者确认，本次不新增开源许可声明。公开来源页面、论文、姓名及数据所涉及的第三方权利不因本仓库改变；不对第三方原文重新授权。事实摘要与链接供研究导航；请独立核实最新来源，不用于自动作出人事或招生决定。

## 可恢复进度

最新独立增量范围见[四川大学十一人增量](progress/independent-scu11-update.md)，前批记录见[东南大学十人](progress/independent-seu10-update.md)、[南京大学后续十人](progress/independent-nju10-update.md)及[社会学院两人](progress/independent-nju-update.md)，测试职责见[历史与当前测试分离](docs/test-scopes.md)。旧批次文档保留原验收时点，不表示最新人数。

见[当前覆盖与核验进度](progress/current-coverage.md)、[任务队列](progress/work-queue.json)及[接续规则](docs/continuation.md)。
