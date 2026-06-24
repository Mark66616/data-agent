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
│   │   ├── llm.py          # LLM 客户端配置
│   │   └── nodes/          # 工作流节点
│   │       ├── extract_keyword.py    # 关键词抽取
│   │       ├── recall_column.py      # 列召回
│   │       ├── recall_metric.py      # 指标召回
│   │       ├── recall_value.py       # 值召回
│   │       ├── merge_recall_info.py  # 合并召回信息
│   │       ├── filter_table.py       # 表过滤
│   │       ├── filter_metric.py      # 指标过滤
│   │       ├── add_context.py        # 上下文构建
│   │       ├── generate_sql.py       # SQL 生成
│   │       ├── validate_sql.py       # SQL 验证
│   │       ├── corrected_sql.py      # SQL 修正
│   │       └── execute_sql.py        # SQL 执行
│   ├── clients/            # 客户端管理
│   │   ├── mysql_client_manager.py   # MySQL 客户端
│   │   ├── qdrant_client_manager.py  # Qdrant 客户端
│   │   ├── es_client_manager.py      # Elasticsearch 客户端
│   │   └── embedding_client_manager.py # Embedding 客户端
│   ├── conf/               # 配置模块
│   │   ├── app_config.py   # 应用配置加载
│   │   └── meta_config.py  # 元数据配置加载
│   ├── core/               # 核心工具
│   │   ├── log.py          # 日志工具
│   │   └── lifespan.py     # FastAPI 生命周期管理
│   ├── entities/           # 实体定义
│   ├── models/             # 数据模型 (SQLAlchemy)
│   ├── reposities/         # 数据仓库层
│   │   ├── mysql/          # MySQL 仓库
│   │   │   ├── meta/       # 元数据仓库
│   │   │   └── dw/         # 数仓仓库
│   │   ├── qdrant/         # Qdrant 仓库
│   │   └── es/             # Elasticsearch 仓库
│   ├── scripts/            # 脚本工具
│   │   └── build_meta_knowledge.py  # 元知识库构建脚本
│   └── services/           # 服务层
│       └── meta_knowledge_service.py # 元知识服务
├── conf/                   # 配置文件目录
│   ├── app_config.yaml     # 应用配置 (数据库、LLM 等)
│   └── meta_config.yaml    # 元数据配置 (表、列、指标定义)
├── prompts/                # Prompt 模板目录
│   ├── generate_sql.prompt
│   ├── validate_sql.prompt
│   └── ...
├── main.py                 # FastAPI 入口
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

- **MySQL 元数据库**: 存储表结构、列信息、指标定义等元数据
- **MySQL 数仓**: 存储实际业务数据
- **Qdrant 向量数据库**: 存储列和指标的向量嵌入
- **Embedding 服务**: 提供文本向量化能力
- **Elasticsearch**: 存储和检索值级别的元数据
- **LLM 服务**: 用于 SQL 生成和修正

> ⚠️ **注意**: 请勿将真实的数据库密码、API Key 等敏感信息提交到版本控制系统。建议使用环境变量或本地配置文件覆盖默认设置。

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

可以通过环境变量覆盖配置文件中的设置。主要支持以下环境变量:

- `DB_META_HOST`, `DB_META_PORT`, `DB_META_USER`, `DB_META_PASSWORD`, `DB_META_DATABASE`
- `DB_DW_HOST`, `DB_DW_PORT`, `DB_DW_USER`, `DB_DW_PASSWORD`, `DB_DW_DATABASE`
- `QDRANT_HOST`, `QDRANT_PORT`
- `EMBEDDING_HOST`, `EMBEDDING_PORT`, `EMBEDDING_MODEL`
- `ES_HOST`, `ES_PORT`, `ES_INDEX_NAME`
- `LLM_MODEL_NAME`, `LLM_API_KEY`, `LLM_BASE_URL`

### 日志配置

日志配置在 `app_config.yaml` 中，支持文件日志和控制台日志:

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
- 根据实际业务场景调整 `meta_config.yaml` 中的配置（表结构、列描述、指标定义等）
- LLM API key 需要替换为有效的密钥
- **安全提示**: 请勿将包含真实密码和密钥的配置文件提交到 Git，建议使用 `.gitignore` 忽略敏感配置文件或使用环境变量注入

## License

MIT
