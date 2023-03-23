from .basic_config import BasicConfig
from .midjourney_config import MidjourneyConfig

CONFIG_CLASSES = {c.__name__: c for c in [BasicConfig, MidjourneyConfig]}
