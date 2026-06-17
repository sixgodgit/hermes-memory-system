# Hermes Memory System

基于 MemPalace 分析启发的 Hermes Agent 记忆系统优化方案。

## 架构

```
记忆系统
├── L0 身份协议层（78 tokens）    ← 核心规则注入
├── L1 AAAK 压缩事实层（142 tokens）← 关键事实 30x 压缩
├── 织线知识图谱                   ← 三元组 + 时间有效性窗口
├── ChromaDB 语义搜索后端          ← 替代 TF-IDF，318 条沙粒
└── Exa 搜索备用                   ← Tavily 挂了自动切
```

## 效果

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| 记忆注入 token | 882 chars | 220 tokens（↓75%） |
| 织线查询 | 全量三元组 | 支持 as_of 时间点 |
| 语义搜索 | 仅 TF-IDF | TF-IDF + ChromaDB 双后端 |
| 搜索可用性 | 仅 Tavily | Tavily → Exa 自动 fallback |

## 文件说明

| 文件 | 用途 |
|------|------|
| `memory_layers/l0_identity.md` | AI 身份、委托协议、对话纪律 |
| `memory_layers/l1_facts.aaak` | 环境/项目/密钥 AAAK 压缩 |
| `memory_layers/persona_combined.md` | 合并 L0+L1+gate 的 persona 文件 |
| `nexsandglass-upgrade/sandglass_chroma.py` | ChromaDB PersistentClient 后端 |
| `nexsandglass-upgrade/weavethread.py` | 织线知识图谱（含 valid_from/until） |
| `nexsandglass-upgrade/sandglass_mcp.py` | MCP Server schema（含新参数） |
| `nexsandglass-upgrade/migrate_to_chromadb.py` | 沙粒 → ChromaDB 迁移脚本 |
| `compress_memory.py` | MEMORY.md → L0/L1 AAAK 自动压缩 |
| `switch_memory_layers.sh` | 启用/禁用分层注入 |
| `tavily_fallback.py` | Tavily 失败自动切 Exa |

## 配合

- **Agent**: Hermes Agent (Nous Research)
- **MCP Server**: NexSandglass（沙漏记忆系统）
- **启发**: MemPalace (mempalace/mempalace)
