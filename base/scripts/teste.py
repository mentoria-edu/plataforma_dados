from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("SimplesTesteDataFrame").getOrCreate()

dados = [(1, "Ana"), (2, "Pedro"), (3, "Maria")]
df = spark.createDataFrame(dados, ["id", "nome"])

df.write.mode("overwrite").saveAsTable("teste_simples")

spark.stop()