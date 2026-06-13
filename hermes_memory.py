#!/usr/bin/env python3
"""
Hermes ChromaDB 记忆系统 — 已归档，仅作资料检索库使用。
不再作为长期人格记忆、当前任务状态、模型调度策略或最终决策依据。

详见 ~/.hermes/memory/README.md 分层架构。

# 记忆系统变更（2026-06-13）
# 
# ChromaDB 已从"主要记忆系统"降级为"资料检索库"。
# 新架构采用分层记忆：
#   - core_memory.md: 长期稳定事实（最高优先级）
#   - task_memory/: 当前任务状态
#   - archive/: 废弃方案历史
#   - vector_knowledge/ + ChromaDB: 仅资料检索
#
# 优先级规则：
#   用户最新指令 > core_memory.md > task_memory > vector search > archive
"""
import os, sys

print("[⚠️ 已废弃] Hermes ChromaDB 记忆系统已降级为资料检索库。")
print("  ChromaDB 仅用于相似资料搜索，不代表用户当前意图。")
print("  长期记忆 → ~/.hermes/memory/core_memory.md")
print("  任务状态 → ~/.hermes/memory/task_memory/")
print("  废弃方案 → ~/.hermes/memory/archive/")
print("  资料检索 → ChromaDB（仅供相似度搜索）")
print()
print("优先级: 用户最新指令 > core_memory.md > task_memory > vector search > archive")
print()

# 保留最小查询功能用作资料检索
if len(sys.argv) > 1 and sys.argv[1] in ("search", "context", "query"):
    try:
        import chromadb
        client = chromadb.PersistentClient(path='/root/.hermes/memory_db')
        col = client.get_collection('hermes_memories')
        query = " ".join(sys.argv[2:])
        n = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[1] in ("search",) else 5
        results = col.query(query_texts=[query], n_results=n)
        if results.get('documents'):
            for i, doc in enumerate(results['documents'][0]):
                dist = results['distances'][0][i] if results.get('distances') else 0
                print(f"\n--- 结果 {i+1} (距离: {dist:.3f}) ---")
                print(doc)
        else:
            print("无匹配结果")
    except Exception as e:
        print(f"查询失败: {e}")
