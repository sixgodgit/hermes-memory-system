# Hermes Memory System

基于 ChromaDB 的语义记忆系统，替代压缩关键词模式。

## 特性

- **语义搜索**：基于 embedding 的相似度搜索，不再依赖关键词匹配
- **自动重要性评分**：记忆自动标记重要性，低重要性记忆定期清理
- **多类型支持**：支持用户偏好、环境信息、梦境洞察等多种类型
- **Token 预算控制**：自动控制注入上下文的 token 数量

## 安装

```bash
pip install chromadb sentence-transformers
```

## 使用

### Python API

```python
from hermes_memory import get_memory

mem = get_memory()

# 添加记忆
mem.add("用户偏好深色主题 UI", {"type": "user_preference", "importance": 0.8})

# 语义搜索
results = mem.search("UI 设计风格", n_results=5)

# 获取上下文（自动控制 token）
context = mem.get_context("用户喜欢什么", max_tokens=2000)
```

### CLI

```bash
# 添加记忆
python3 hermes_memory.py add "用户偏好深色主题" "user_preference" 0.8

# 搜索
python3 hermes_memory.py search "UI 设计" 5

# 获取上下文
python3 hermes_memory.py context "用户喜欢什么"

# 统计
python3 hermes_memory.py stats

# 清理旧记忆
python3 hermes_memory.py cleanup 30
```

## 数据库位置

`~/.hermes/memory_db/`

## 与 Hermes Agent 集成

1. 在 cron job 中调用 `hermes_memory.py` 存储每日洞察
2. 在对话开始时调用 `get_context()` 获取相关记忆
3. 定期调用 `cleanup()` 清理过时记忆

## License

CC BY-NC 4.0 - Author: sixgod
