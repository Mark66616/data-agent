from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.reposities.mysql.meta.column_info_mapper import ColumnInfoMapper
from app.reposities.mysql.meta.table_info_mapper import TableInfoMapper


class MetaSqlRepository:
    def __init__(self, seesion: AsyncSession):
        self.session = seesion

    def save_table_infos(self, table_infos: list[TableInfo]):
        self.session.add_all([TableInfoMapper.to_model(table_info) for table_info in table_infos])

    def save_column_infos(self, column_infos: list[ColumnInfo]):
        self.session.add_all([ColumnInfoMapper.to_model(column_info) for column_info in column_infos])
