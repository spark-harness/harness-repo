# Requirements

`requirements/` 保存每个需求的生命周期产物。

推荐结构：

```text
requirements/{requirement-id}/
├── README.md
├── requirement.md
├── impact-analysis.md
├── design.md
├── tasks.json
├── gates/
└── reviews/
```

## 使用规则

- 一个需求一个目录。
- 需求、设计、任务、门禁和评审记录必须能相互追溯。
- 阶段推进以 `context/harness-framework/main-process-numbering.md` 为准。
- 门禁报告写入 `gates/`，审查报告写入 `reviews/`。
