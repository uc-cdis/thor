from starlette.config import Config

config = Config(".env")

username = config("username", cast=str, default="postgress")
password = config("password", cast=str, default="")
IPadd = config("IPadd", cast=str, default="localhost")
portNum = config("portNum", cast=str, default="5432")
DBname = config("DBname", cast=str, default="thor_test_tmp")
