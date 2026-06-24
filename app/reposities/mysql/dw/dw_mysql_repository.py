from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.state import DbInfoState


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

    async def get_db_info(self) -> DbInfoState:
        result = await self.session.execute(text("select version()"))

        version = result.scalar()

        dialect = self.session.get_bind().dialect.name

        return DbInfoState(dialect=dialect, version=version)

    async def validate_sql(self, generated_sql):
        await self.session.execute(text("explain " + generated_sql))

    async def execute_sql(self, generated_sql:str) -> list[dict]:
        result = await self.session.execute(text(generated_sql))
        return [dict(row) for row in result.fetchall()]
