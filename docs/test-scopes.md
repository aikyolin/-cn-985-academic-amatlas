# 历史版本与当前版本测试

旧版本来源契约保持原有固定值，不通过改写旧哈希容纳新资料。`tests/fixtures/released-1458f458.zip` 是已发布提交 `1458f4584a52a448461a5f72489efdc873305bd8` 的 410 个文件；建立时逐个与远端 Git blob 核对，测试运行时校验压缩包固定摘要。旧元数据迁移验证器要求完整 410 文件清单，所以本夹具保留完整历史输入，只用于测试，不放入 `site/`。

只有明确声称“历史版本精确字节、旧批次完整后缀、旧元数据迁移整树”的断言，显式读取 `published_root()`／`publishedRoot()`。旧来源契约、固定哈希、反例及历史验证器未改写。JS 显示兼容测试使用历史输入时，仍导入当前 `site/model.js` 和 `site/app.js`。

当前代码、规范数据、生成快照、完整 JSON Schema、来源闭包、导出、筛选、转义及导航测试仍针对实际工作树。`tests/test_current_release.py` 明确校验当前 614 人与旧 612 人的精确增量守恒、独立来源映射、旧工作簿字节、实际构建标识和当前全量验证；`tests/current-release.test.js` 使用当前生成数据与当前应用代码测试两个人物的实际展示与筛选。

运行全部测试，不跳过旧测试：

```sh
npm test
python -m unittest discover -s tests -v
python scripts/build.py
python scripts/validate_queue.py progress/work-queue.json --check-artifacts
```

历史夹具通过不等于当前版本通过。两类结果必须都通过；不能将干净历史数据当作当前候选的验证输入，也不能重新签署旧契约、略过失败断言或把来源审查当作工程验收。新增来源映射仍需独立事实复核。
