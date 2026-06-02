# Skills

Skill 是可复用工作流。它描述“做一类事时应该按什么步骤收敛上下文、产出文件、通过门禁”。

建议按领域拆分：

```text
skills/
├── managing-requirement-lifecycle/
├── traceability-gate-checker/
├── service-repo-check/
└── self-refinement/
```

最小落地时，先维护 `managing-requirement-lifecycle`，保证需求阶段推进口径一致。
