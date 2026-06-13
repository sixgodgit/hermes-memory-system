# Hermes Memory System ⚠️ 已归档

> **状态更新（2026-06-13）：ChromaDB 已从"主要记忆系统"降级为"资料检索库"。**

## 变更说明

旧方案中 ChromaDB 承载了所有记忆功能：用户偏好、环境信息、任务状态、对话历史。这导致了上下文混乱和记忆污染问题（重复回答已解决的问题、旧策略污染当前决策）。

### 新架构

采用分层记忆结构 (`~/.hermes/memory/`)：

```
core_memory.md      — 长期稳定事实，最高优先级
task_memory/        — 当前任务状态，每个任务独立文件
archive/            — 废弃方案、失败方案、历史方案（默认不读取）
vector_knowledge/   — ChromaDB 仅用于资料检索，不作决策依据
```

### 优先级规则

> **用户最新明确指令 > core_memory.md > task_memory > vector search > archive**

- ChromaDB 检索结果与 core_memory.md 冲突时 → 以 core_memory.md 为准
- 旧记忆与用户最新指令冲突时 → 以用户最新指令为准
- archive 默认禁止读取，除非用户明确要求回顾历史

## 保留功能（降级后）

ChromaDB 仍可作资料检索库使用：

```bash
python3 hermes_memory.py search "关键词"
python3 hermes_memory.py context "关键词"
```

## 不再支持的功能

- ❌ 自动写入对话内容到 ChromaDB
- ❌ 把 ChromaDB 检索结果当作长期偏好
- ❌ 通过 ChromaDB 管理任务状态
- ❌ ChromaDB 作为决策依据

## 历史

- **v1.0** (2026-06-10)：基于 ChromaDB 的语义记忆系统
- **v1.0-archived** (2026-06-13)：降级为资料检索库，改用分层记忆架构

## License

CC BY-NC 4.0 - Author: sixgod
