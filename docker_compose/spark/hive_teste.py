from pyspark.sql import SparkSession

metastore_host = "masternode"
metastore_port = "9083"

spark = (
    SparkSession.builder
        .appName("SparkRemoteHiveMetastoreTest")
        # .config("spark.sql.hive.metastore.jars", "builtin")  # Descomente se necessário
        .config("hive.metastore.uris", f"thrift://masternode:9083")
        .enableHiveSupport()
        .getOrCreate()
)

warehouse_dir = spark.conf.get("spark.sql.warehouse.dir")
print(f"Diretório warehouse configurado: {warehouse_dir}")
print(f"Conectado ao Hive Metastore em: thrift://{metastore_host}:{metastore_port}")

dados = [(1, "Nome_1"), (2, "Nome_2"), (3, "Nome_3")]
df = spark.createDataFrame(dados, ["id", "nome"])

df.write.mode("overwrite").saveAsTable("teste_simples")

print("DataFrame salvo com sucesso no Hive Metastore remoto!")
spark.stop()