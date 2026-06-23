# Data Agent

一个基于 LangGraph 构建的智能数据查询 Agent，支持通过自然语言查询数据库并自动生成和执行 SQL。

## 功能特性

- 🤖 **智能 SQL 生成**: 使用 LLM 将自然语言转换为 SQL 查询
- 🔍 **多路召回**: 支持列、指标、值的向量召回和语义搜索
- 📊 **数据可视化**: 支持查询结果的分析与展示
- 🔁 **SQL 校验与修正**: 自动验证生成的 SQL 并在错误时进行修正
- 🗄️ **多数据源支持**: 
  - MySQL (元数据和数仓)
  - Qdrant (向量数据库)
  - Elasticsearch (全文检索)
- 🎯 **关键词抽取**: 基于 jieba 的中文关键词提取

## 系统架构

```
用户查询 → 关键词抽取 → 多路召回 → 信息过滤 → 上下文构建 → SQL 生成 → 校验 → 执行
                         ↓
                    列召回 / 指标召回 / 值召回
```

### Agent 工作流程

1. **extract_keyword**: 从用户查询中提取关键词
2. **recall_column/metric/value**: 并行召回相关的列、指标和值
3. **merge_recall_info**: 合并召回的信息
4. **filter_table/metric**: 过滤相关的表和指标
5. **add_context**: 构建 SQL 生成的上下文
6. **generate_sql**: 生成 SQL 查询
7. **validate_sql**: 验证 SQL 的正确性
8. **corrected_sql**: (条件分支) 如果验证失败则修正 SQL
9. **execute_sql**: 执行 SQL 并返回结果

## 技术栈

- **Python** >= 3.12
- **LangGraph** >= 1.2.4 - Agent 工作流编排
- **LangChain** >= 1.3.4 - LLM 应用框架
- **FastAPI** >= 0.136.3 - Web 框架
- **SQLAlchemy** >= 2.0.50 - ORM
- **Qdrant** >= 1.18.0 - 向量数据库
- **Elasticsearch** >= 8.x - 搜索引擎
- **MySQL** (asyncmy) - 关系型数据库
- **jieba** - 中文分词和关键词提取
- **Loguru** - 日志管理
- **OmegaConf** - 配置管理

## 项目结构

```
.
├── app/
│   ├── agent/              # Agent 核心逻辑
│   │   ├── graph.py        # LangGraph 工作流定义
│   │   ├── state.py        # Agent 状态定义
│   │   ├── context.py      # Agent 上下文定义
│   │   └── nodes/          # 工作流节点
│   │       ├── extract_keyword.py
│   │       ├── recall_column.py
│   │       ├── recall_metric.py
│   │       ├── recall_value.py
│   │       ├── merge_recall_info.py
│   │       ├── filter_table.py
│   │       ├── filter_metric.py
│   │       ├── add_context.py
│   │       ├── generate_sql.py
│   │       ├── validate_sql.py
│   │       ├── corrected_sql.py
│   │       └── execute_sql.py
│   ├── clients/            # 客户端管理
│   │   ├── mysql_client_manager.py
│   │   ├── qdrant_client_manager.py
│   │   ├── es_client_manager.py
│   │   └── embedding_client_manager.py
│   ├── conf/               # 配置模块
│   │   ├── app_config.py
│   │   └── meta_config.py
│   ├── core/               # 核心工具
│   │   └── log.py
│   ├── entities/           # 实体定义
│   ├── models/             # 数据模型
│   ├── reposities/         # 数据仓库层
│   │   ├── mysql/
│   │   ├── qdrant/
│   │   └── es/
│   ├── scripts/            # 脚本工具
│   │   └── build_meta_knowledge.py
│   └── services/           # 服务层
│       └── meta_knowledge_service.py
├── conf/                   # 配置文件
│   ├── app_config.yaml     # 应用配置
│   └── meta_config.yaml    # 元数据配置
├── pyproject.toml          # 项目依赖
└── uv.lock                 # 依赖锁定文件
```

## 快速开始

### 安装依赖

```bash
# 使用 uv 安装 (推荐)
uv sync

# 或使用 pip
pip install -e .
```

### 配置

编辑 `conf/app_config.yaml` 配置以下服务:

```yaml
# MySQL 配置 (元数据库)
db_meta:
  host: localhost
  port: 3306
  user: your_user
  password: your_password
  database: meta

# MySQL 配置 (数仓)
db_dw:
  host: localhost
  port: 3306
  user: your_user
  password: your_password
  database: dw

# Qdrant 向量数据库配置
qdrant:
  host: localhost
  port: 6333
  embedding_size: 1024

# Embedding 服务配置
embedding:
  host: localhost
  port: 8081
  model: BAAI/bge-large-zh-v1.5

# Elasticsearch 配置
es:
  host: localhost
  port: 9200
  index_name: data_agent

# LLM 配置
llm:
  model_name: gpt-5.2-codex
  api_key: <your_api_key>
  base_url: https://api.openai-proxy.org/v1
```

### 构建元知识库

在运行 Agent 之前，需要先构建元知识库:

```bash
cd app
python scripts/build_meta_knowledge.py -p ../conf/meta_config.yaml
```

### 运行 Agent

```python
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.agent.context import DataAgentContext

async def query():
    state = DataAgentState(
        user_query='统计华北地区当前季度销售排名前 3 名的商品',
        error=None
    )
    context = DataAgentContext()
    
    async for chunk in graph.astream(input=state, context=context, stream_mode='custom'):
        print(chunk)

import asyncio
asyncio.run(query())
```

## 配置说明

### 环境变量

可以通过环境变量覆盖配置文件中的设置。

### 日志配置

日志配置在 `app_config.yaml` 中:

```yaml
logging:
  file:
    enable: true
    level: INFO
    path: logs
    rotation: "10 MB"
    retention: "7 days"
  console:
    enable: true
    level: INFO
```

## 开发指南

### 添加新的处理节点

1. 在 `app/agent/nodes/` 目录下创建新的节点文件
2. 实现节点函数，遵循 `(state, runtime) -> dict` 签名
3. 在 `graph.py` 中添加节点和边

### 自定义召回策略

修改 `recall_column.py`, `recall_metric.py`, `recall_value.py` 来实现不同的召回逻辑。

### 调整 SQL 生成提示词

修改 `generate_sql.py` 中的 prompt 模板来优化 SQL 生成效果。

## 注意事项

- 确保所有外部服务 (MySQL, Qdrant, Elasticsearch, Embedding 服务) 已启动并可访问
- 首次使用前必须运行 `build_meta_knowledge.py` 构建元知识库
- 根据实际业务场景调整 `meta_config.yaml` 中的配置
- LLM API key 需要替换为有效的密钥

## License

MIT
