from pathlib import Path

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.models.column_info import ColumnInfoMySQL
from app.models.table_info import TableInfoMySQL
from app.reposities.mysql.dw.dw_mysql_repository import DwMsqlRepository
from app.reposities.mysql.meta.meta_sql_repository import MetaSqlRepository


class MateKnowledgeService:
    def __init__(self
                 , meta_sql_repository: MetaSqlRepository
                 , dw_sql_repository: DwMsqlRepository
                 ):
        self.meta_sql_repository: MetaSqlRepository = meta_sql_repository
        self.dw_sql_repository: DwMsqlRepository = dw_sql_repository

    async def build(self, config_path: Path):
        logger.info(f"读取元知识库配置文件: {config_path}")
        # 读取yaml
        conf = OmegaConf.load(config_path)
        # 定义实体类结构
        schema = OmegaConf.structured(MetaConfig)
        # 将配置文件绑定实体类结构
        # merge中要先放schema，再放conf，否则会取schema中的默认参数None
        omega_config = OmegaConf.merge(schema, conf)
        # 加载yaml并赋值给实体类
        meta_config: MetaConfig = OmegaConf.to_object(omega_config)
        # logger.info(meta_config)

        # 根据配置文件同步指定的元数据库和向量索引以及全文索引
        if meta_config.tables:
            table_infos: list[TableInfo] = []
            column_infos: list[ColumnInfo] = []

            for table in meta_config.tables:
                table_info = TableInfo(id=table.name, name=table.name, role=table.role,
                                            description=table.description)
                table_infos.append(table_info)

                # 查询表结构字段类型
                column_types = await self.dw_sql_repository.get_table_columns(table.name)

                for column in table.columns:
                    # 查询字段取值示例
                    column_examples = await self.dw_sql_repository.get_column_examples(table.name, column.name)

                    column_info = ColumnInfo(id=f"{table.name}.{column.name}", name=column.name,
                                                  type=column_types[column.name], role=column.role,
                                                  examples=column_examples, description=column.description,
                                                  alias=column.alias, table_id=table.name)
                    column_infos.append(column_info)

            # 保存表结构，使用自动提交事物，有异常自动会滚
            async with self.meta_sql_repository.session.begin():
                self.meta_sql_repository.save_table_infos(table_infos)
                self.meta_sql_repository.save_column_infos(column_infos)
            # 将关键字段信息进行向量化并存储到数据库

            # 对维度字段信息创建全文索引并保存在es中

        if meta_config.metrics:
            for metrics in meta_config.metrics:
                # 将指标信息同步到meta数据库中

                # 将指标信息进行向量化并存储到数据库
                print(metrics)
