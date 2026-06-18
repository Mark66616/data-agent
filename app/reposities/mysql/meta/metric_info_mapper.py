from dataclasses import asdict

from app.entities.metric_info import MetricInfo
from app.models.metric_info import MetricInfoMySQL


class MetricInfoMapper:
    @staticmethod
    def to_entity(metric_info: MetricInfoMySQL) -> MetricInfo:
        return MetricInfo(
            id=metric_info.id,
            name=metric_info.name,
            description=metric_info.description,
            relevant_columns=metric_info.relevant_columns,
            alias=metric_info.alias
        )

    @staticmethod
    def to_model(metric_info: MetricInfo) -> MetricInfoMySQL:
        return MetricInfoMySQL(**asdict(metric_info))
