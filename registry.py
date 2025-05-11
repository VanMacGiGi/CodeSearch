import logging

logger = logging.getLogger('registry')


class Registry:
    _registry = {}

    @classmethod
    def register(cls, extensions):
        def decorator(lang_cls):
            logger.debug(f"Register {extensions} for {lang_cls}")
            for ext in extensions:
                cls._registry[ext] = lang_cls
            return lang_cls
        return decorator

    @classmethod
    def get_lang_for(cls, filename):
        logger.info(f"Get language for {filename}")
        for ext, lang_cls in cls._registry.items():
            logger.debug(f"Ext = {ext}, Class = {lang_cls}")
            if filename.endswith(f".{ext}"):
                logger.info(f"Found for extension {ext} language {lang_cls}")
                return lang_cls
        return None
