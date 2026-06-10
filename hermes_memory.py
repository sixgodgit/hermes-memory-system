#!/usr/bin/env python3
"""
Hermes ChromaDB 记忆系统
基于语义搜索的长期记忆，替代压缩关键词模式
"""
import os, json, time, hashlib
from datetime import datetime
from pathlib import Path

# ChromaDB 和 Embedding
import chromadb
from chromadb.config import Settings

# 配置
DB_PATH = os.path.expanduser("~/.hermes/memory_db")
COLLECTION_NAME = "hermes_memories"

class HermesMemory:
    """Hermes 语义记忆系统"""
    
    def __init__(self):
        """初始化 ChromaDB 客户端"""
        os.makedirs(DB_PATH, exist_ok=True)
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
        print(f"[Memory] 初始化完成，当前记忆数: {self.collection.count()}")
    
    def add(self, content: str, metadata: dict = None):
        """
        添加记忆
        content: 记忆内容（自然语言）
        metadata: 元数据（来源、时间、类型等）
        """
        if not content or not content.strip():
            return None
        
        # 生成唯一 ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        timestamp = int(time.time())
        doc_id = f"mem_{timestamp}_{content_hash}"
        
        # 默认元数据
        meta = {
            "created_at": datetime.now().isoformat(),
            "timestamp": timestamp,
            "type": metadata.get("type", "general") if metadata else "general",
            "importance": metadata.get("importance", 0.5) if metadata else 0.5,
        }
        if metadata:
            meta.update(metadata)
        
        # 添加到 ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=[meta],
            ids=[doc_id]
        )
        
        print(f"[Memory] 添加: {doc_id} | {content[:50]}...")
        return doc_id
    
    def search(self, query: str, n_results: int = 5, filter_type: str = None):
        """
        语义搜索记忆
        query: 查询内容
        n_results: 返回结果数
        filter_type: 按类型过滤
        """
        if not query or not query.strip():
            return []
        
        where = {"type": filter_type} if filter_type else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        memories = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                memories.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })
        
        return memories
    
    def get_context(self, query: str, max_tokens: int = 2000):
        """
        获取相关记忆上下文（用于注入 system prompt）
        自动控制 token 预算
        """
        memories = self.search(query, n_results=10)
        
        if not memories:
            return ""
        
        # 按相关性排序，过滤距离太远的
        relevant = [m for m in memories if m["distance"] < 0.8]
        
        # 构建上下文，控制 token
        context_parts = []
        current_tokens = 0
        
        for mem in relevant:
            # 粗略估算 token（中文约 1.5 token/字）
            est_tokens = len(mem["content"]) * 1.5
            
            if current_tokens + est_tokens > max_tokens:
                break
            
            context_parts.append(mem["content"])
            current_tokens += est_tokens
        
        if not context_parts:
            return ""
        
        return "\n".join(context_parts)
    
    def delete(self, doc_id: str):
        """删除记忆"""
        try:
            self.collection.delete(ids=[doc_id])
            print(f"[Memory] 删除: {doc_id}")
            return True
        except Exception as e:
            print(f"[Memory] 删除失败: {e}")
            return False
    
    def update(self, doc_id: str, content: str, metadata: dict = None):
        """更新记忆"""
        try:
            meta = metadata or {}
            meta["updated_at"] = datetime.now().isoformat()
            
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[meta] if meta else None
            )
            print(f"[Memory] 更新: {doc_id}")
            return True
        except Exception as e:
            print(f"[Memory] 更新失败: {e}")
            return False
    
    def count(self):
        """获取记忆总数"""
        return self.collection.count()
    
    def list_all(self, limit: int = 100):
        """列出所有记忆"""
        results = self.collection.get(limit=limit)
        memories = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"]):
                memories.append({
                    "id": results["ids"][i],
                    "content": doc,
                    "metadata": results["metadatas"][i] if results["metadatas"] else {}
                })
        return memories
    
    def cleanup(self, days: int = 30):
        """清理旧记忆"""
        cutoff = int(time.time()) - (days * 86400)
        all_mems = self.list_all(limit=1000)
        
        deleted = 0
        for mem in all_mems:
            ts = mem["metadata"].get("timestamp", 0)
            importance = mem["metadata"].get("importance", 0.5)
            
            # 低重要性且超过天数的删除
            if ts < cutoff and importance < 0.7:
                self.delete(mem["id"])
                deleted += 1
        
        print(f"[Memory] 清理完成，删除 {deleted} 条旧记忆")
        return deleted
    
    def stats(self):
        """获取统计信息"""
        all_mems = self.list_all(limit=1000)
        
        types = {}
        for mem in all_mems:
            t = mem["metadata"].get("type", "unknown")
            types[t] = types.get(t, 0) + 1
        
        return {
            "total": len(all_mems),
            "by_type": types,
            "db_path": DB_PATH
        }


# 全局实例
_memory_instance = None

def get_memory():
    """获取记忆系统单例"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = HermesMemory()
    return _memory_instance


# CLI 入口
if __name__ == "__main__":
    import sys
    
    mem = get_memory()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 hermes_memory.py add <content> [type] [importance]")
        print("  python3 hermes_memory.py search <query> [n_results]")
        print("  python3 hermes_memory.py context <query>")
        print("  python3 hermes_memory.py stats")
        print("  python3 hermes_memory.py list")
        print("  python3 hermes_memory.py cleanup [days]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "add":
        content = sys.argv[2] if len(sys.argv) > 2 else ""
        mem_type = sys.argv[3] if len(sys.argv) > 3 else "general"
        importance = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
        mem.add(content, {"type": mem_type, "importance": importance})
    
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        results = mem.search(query, n)
        for r in results:
            print(f"[{r['id']}] (dist={r['distance']:.3f}) {r['content'][:100]}")
    
    elif cmd == "context":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        ctx = mem.get_context(query)
        print(ctx if ctx else "无相关记忆")
    
    elif cmd == "stats":
        s = mem.stats()
        print(f"总记忆数: {s['total']}")
        print(f"按类型: {s['by_type']}")
        print(f"数据库: {s['db_path']}")
    
    elif cmd == "list":
        mems = mem.list_all()
        for m in mems:
            print(f"[{m['id']}] {m['content'][:80]}")
    
    elif cmd == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        mem.cleanup(days)
    
    else:
        print(f"未知命令: {cmd}")
