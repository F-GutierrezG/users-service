class BaseConfig:
    """ Base configuration """
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """ Development configuration """
    pass


class TestingConfig(BaseConfig):
    """ Testing configuration """
    TESTING = True


class StagingConfig(BaseConfig):
    """ Staging configuration """
    pass


class ProductionConfig(BaseConfig):
    """ Production configuration """
    DEBUG = False
