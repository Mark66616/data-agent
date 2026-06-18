import argparse
import asyncio
from pathlib import Path

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.core.log import logger
from app.reposities.es.value_es_repository import ValueEsRepository
from app.reposities.mysql.dw.dw_mysql_repository import DwMsqlRepository
from app.reposities.mysql.meta.meta_sql_repository import MetaSqlRepository
from app.reposities.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.services.meta_knowledge_service import MateKnowledgeService


async def build(config_path: Path):
    logger.info(f"开始构建元知识库: {config_path}")
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()
    qdrant_client_manager.init()
    embedding_client_manager.init()
    es_client_manager.init()

    async with (meta_mysql_client_manager.session_factory() as meta_session
        , dw_mysql_client_manager.session_factory() as dw_session):
        meta_sql_repository = MetaSqlRepository(meta_session)
        dw_sql_repository = DwMsqlRepository(dw_session)

        column_qdrant_repository = ColumnQdrantRepository(qdrant_client_manager.client)
        embedding_client = embedding_client_manager.client
        value_es_repository = ValueEsRepository(es_client_manager.client)

        # 执行元数据库构建方法
        meta_knowledge_service = MateKnowledgeService(meta_sql_repository=meta_sql_repository
                                                      , dw_sql_repository=dw_sql_repository
                                                      , column_qdrant_repository=column_qdrant_repository
                                                      , embedding_client=embedding_client
                                                      , value_es_repository=value_es_repository
                                                      )
        logger.info("元数据库构建方法开始执行")
        await meta_knowledge_service.build(config_path)

    await meta_mysql_client_manager.close()
    await dw_mysql_client_manager.close()
    await qdrant_client_manager.close()
    await es_client_manager.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # 可选参数
    parser.add_argument('-p', '--path')

    args = parser.parse_args()

    print(args)
    config_path = args.path

    print(Path("conf/meta_config.yaml"))

    asyncio.run(build(Path(config_path)))
