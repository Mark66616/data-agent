from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DwMsqlRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_table_columns(self, table_name) -> dict[str, str]:
        sql = f"show columns from {table_name}"
        results = await self.session.execute(text(sql))
        result_dict = results.mappings().fetchall()

        return {result['Field']: result['Type'] for result in result_dict}

    async def get_column_examples(self, table_name, column_name, limit=10):
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        results = await self.session.execute(text(sql))
        return [result[0] for result in results.fetchall()]