from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class MetaSqlRepository:
    def __init__(self, seesion: AsyncSession):
        self.session = seesion


