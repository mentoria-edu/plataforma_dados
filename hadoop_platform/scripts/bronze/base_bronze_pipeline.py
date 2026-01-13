from abc import ABC, abstractmethod
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col,
    current_timestamp,
    from_utc_timestamp,
    lit,
    xxhash64
)
from pyspark.sql.types import StructType
from datetime import datetime
from typing import Dict


class BaseBronzePipeline(ABC):
    """Base class for bronze layer ingestion pipelines.
    
    This class implements the Template Method pattern, providing a fixed pipeline
    structure while allowing subclasses to customize specific behaviors through
    abstract and hook methods.
    
    Attributes:
        DATABASE_NAME: The name of the bronze database.
        spark: Active Spark session.
        schema_name: Name of the schema/domain (e.g., 'br_companies').
        table_name: Name of the table (e.g., 'legal_nature').
        bronze_table_name: Full qualified table name in format 'database.schema__table'.
        
    Example:
        >>> class MyPipeline(BaseBronzePipeline):
        ...     def define_schema(self):
        ...         return StructType([...])
        ...     
        ...     def define_primary_key_column(self):
        ...         return "id"
        >>> 
        >>> spark = SparkSession.builder.getOrCreate()
        >>> pipeline = MyPipeline(spark, "my_schema", "my_table")
        >>> pipeline.run("/path/to/file.csv", "2024-12")
    """
    
    DATABASE_NAME = "bronze"
    
    def __init__(
        self, 
        spark: SparkSession, 
        schema_name: str,
        table_name: str,
    ):
        """Initialize the bronze pipeline.
        
        Args:
            spark: Active Spark session for data processing.
            schema_name: Name of the schema/domain (e.g., 'br_companies').
            table_name: Name of the table (e.g., 'legal_nature').
        """
        self.spark = spark
        self.schema_name = schema_name
        self.table_name = table_name
        self._column_hash_name = "_attribute_change_hash"
        self.bronze_table_name = f"{self.DATABASE_NAME}.{self.schema_name}__{self.table_name}"

    @abstractmethod
    def define_schema(self) -> StructType:
        """Define and return the schema structure for the CSV data.
        
        This method must be implemented by subclasses to specify the structure
        of the input CSV file.
        
        Returns:
            StructType: PySpark schema definition with all columns and types.
            
        Example:
            >>> def define_schema(self):
            ...     return StructType([
            ...         StructField("id", StringType(), True),
            ...         StructField("name", StringType(), True),
            ...     ])
        """
        pass
    
    @abstractmethod
    def define_primary_key_column(self) -> str:
        """Return the primary key column name for this table.
        
        Returns:
            str: Name of the primary key column.
        """
        pass
    
    def configure_csv_options(
        self,
        sep: str = ";",
        header: str = "false",
        encoding: str = "UTF-8",
        **kwargs
    ) -> Dict[str, str]:
        """Configure and return CSV reading options.
        
        Args:
            sep: Column separator character. Defaults to ";".
            header: Whether CSV has header row. Defaults to "false".
            encoding: Character encoding of the file. Defaults to "UTF-8".
            **kwargs: Additional CSV reading options to pass to Spark.
        
        Returns:
            Dict[str, str]: Dictionary with CSV reading options.
        """
        return {
            "sep": sep,
            "header": header,
            "encoding": encoding,
            **kwargs
        }
    
    def configure_hudi_options(self) -> Dict[str, str]:
        """Configure and return Hudi write options.
        
        Returns:
            Dict[str, str]: Dictionary with Hudi configuration options.
        """
        record_key = f"{self.define_primary_key_column()},{self._column_hash_name}"
        
        return {
            "hoodie.table.name": self.table_name,
            "hoodie.datasource.write.keygenerator.class": "org.apache.hudi.keygen.ComplexKeyGenerator",
            "hoodie.datasource.write.recordkey.field": record_key,
            "hoodie.datasource.write.partitionpath.field": "_partition_month",
            "hoodie.datasource.write.operation": "insert_overwrite",
            "hoodie.datasource.write.table.type": "COPY_ON_WRITE",
            "hoodie.datasource.write.precombine.field": "_batch_timestamp",
            "hoodie.datasource.hive_sync.enable": "false",
            "hoodie.spark.sql.merge.into.partial.updates": "false",
            "hoodie.cleaner.policy.failed.writes": "LAZY"
        }
    
    def transform_date(self, batch_month: str) -> int:
        """Convert batch month string to integer partition format.
        
        Args:
            batch_month: Date string in YYYY-MM format (e.g., '2024-12').
            
        Returns:
            int: Partition month in YYYYMM format (e.g., 202412).
            
        Raises:
            ValueError: If batch_month is not in YYYY-MM format.
        """
        try:
            datetime.strptime(batch_month, "%Y-%m")
            return int(batch_month.replace("-", ""))
        except Exception:
            raise ValueError(
                f"Invalid date format. Expected ISO pattern YYYY-MM but received: {batch_month}"
            )
    
    def read_csv_file(self, path: str) -> DataFrame:
        """Read CSV file into a DataFrame.
        
        Args:
            path: Path to the CSV file (local or cloud storage).
            
        Returns:
            DataFrame: Raw CSV data as DataFrame with defined schema.
        """
        return (
            self.spark.read.format("csv")
            .options(**self.configure_csv_options())
            .schema(self.define_schema())
            .load(path)
        )
    
    def add_attribute_hash(self, df: DataFrame) -> DataFrame:
        """Add attribute change hash column to DataFrame.
        
        Args:
            df: Source DataFrame with business columns.
            
        Returns:
            DataFrame: DataFrame with _attribute_change_hash column added.
        """
        business_cols = [c for c in df.columns if not c.startswith("_")]
        
        return df.withColumn(
            self._column_hash_name,
            xxhash64(*[col(c) for c in business_cols])
        )
    
    def add_temporal_columns(self, df: DataFrame, partition_month_int: int) -> DataFrame:
        """Add batch timestamp and partition month columns to DataFrame.
        
        Args:
            df: Source DataFrame.
            partition_month_int: Partition month in YYYYMM format.
            
        Returns:
            DataFrame: DataFrame with _batch_timestamp and _partition_month columns.
        """
        return (
            df.withColumn(
                "_batch_timestamp",
                from_utc_timestamp(current_timestamp(), "America/Sao_Paulo"),
            )
            .withColumn("_partition_month", lit(partition_month_int))
        )
    
    def add_scd2_metadata_columns(self, df: DataFrame) -> DataFrame:
        """Add SCD2 metadata columns.
        
        Args:
            df: Source DataFrame.
            
        Returns:
            DataFrame: DataFrame with _is_current column added.
        """
        return df.withColumn("_is_current", lit(True))
    
    def apply_transformations(self, df: DataFrame, partition_month_int: int) -> DataFrame:
        """Apply all standard transformations to the DataFrame.
        
        Args:
            df: Raw DataFrame from CSV.
            partition_month_int: Partition month in YYYYMM format.
            
        Returns:
            DataFrame: Fully transformed DataFrame ready for persistence.
        """
        df = self.add_attribute_hash(df)
        df = self.add_temporal_columns(df, partition_month_int)
        df = self.add_scd2_metadata_columns(df)
        return df
    
    def write_to_hudi(self, df: DataFrame) -> None:
        """Write DataFrame to Hudi table in bronze layer.
        
        Args:
            df: Transformed DataFrame ready to be persisted.
            
        Returns:
            None
        """
        hudi_options = self.configure_hudi_options()
        
        if self.spark.catalog.tableExists(self.bronze_table_name):
            df.write.format("hudi")\
                .mode("append")\
                .options(**hudi_options)\
                .insertInto(self.bronze_table_name)
            return 

        df.write.format("hudi")\
            .mode("overwrite")\
            .options(**hudi_options)\
            .option("hoodie.datasource.write.operation", "bulk_insert")\
            .saveAsTable(self.bronze_table_name)
    
    def run(self, csv_path: str, batch_month: str) -> None:
        """Execute the complete bronze layer ingestion pipeline.
        
        Args:
            csv_path: Path to the CSV file to be ingested.
            batch_month: Batch month in YYYY-MM format (e.g., '2024-12').
            
        Returns:
            None
            
        Raises:
            ValueError: If batch_month format is invalid.
        """
        partition_month_int = self.transform_date(batch_month)
        df = self.read_csv_file(csv_path)
        df = self.apply_transformations(df, partition_month_int)
        self.write_to_hudi(df)