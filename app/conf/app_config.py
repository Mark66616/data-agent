from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf


@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    enable: bool
    level: str


@dataclass
class LoggingConfig:
    file: File
    console: Console


# 数据库配置
@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int


@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str


@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str


@dataclass
class LLMConfig:
    model_name: str
    api_key: str
    base_url: str


@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


# python中的相对路径不是按照本文件为起点，而是按照项目根目录为起点
# 下边的写法是错误的
# conf = OmegaConf.load("../../../conf/app_config.yaml")

# 使用Path模块加载config文件(两种写法)
# __file__代表当前文件的绝对路径
# 写法1:
# path1 = Path(__file__).parent.parent.parent / "conf/app_config.yaml"
# 写法2:parents[n]表示获取当前文件路径的父级路径n层,从0开始代表文件当前处于的文件夹
path2 = Path(__file__).parents[2] / "conf/app_config.yaml"

# 字典类型的返回值，所以以字典类型访问
conf = OmegaConf.load(path2)

schema = OmegaConf.structured(AppConfig)

# merge中要先放schema，再放conf，否则会取schema中的默认参数None
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(schema,conf))
