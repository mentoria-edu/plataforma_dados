#import org.apache.spark.sql.SparkSession
from pyspark.sql import SparkSession # type: ignore

spark_hive_config = (
    SparkSession.builder()
        .appName("teste_2")
        .config("spark.sql.catalogImplementation", "hive")
        .config("spark.sql.hive.metastore.version", "4.0.1")
        .config("spark.sql.hive.metastore.jars", "path")
        .config("spark.sql.hive.metastore.jars", "/opt/spark/jars/hive-metastore-4.0.1.jar")
        .config("hive.metastore.uris", f"thrift://masternode:9083")
        .getOrCreate()
)

# spark = (
#     SparkSession.builder
#         .appName("SparkRemoteHiveMetastoreTest")
#         # .config("spark.sql.hive.metastore.jars", "builtin")  # Descomente se necessário
#         .config("hive.metastore.uris", f"thrift://masternode:9083")
#         .enableHiveSupport()
#         .getOrCreate()
# )

dados = [(1, "Nome_1"), (2, "Nome_2"), (3, "Nome_3")]
df = spark_hive_config.createDataFrame(dados, ["id", "nome"])

df.write.mode("overwrite").saveAsTable("teste_simples")

print("DataFrame salvo com sucesso no Hive Metastore remoto!")
spark_hive_config.stop()