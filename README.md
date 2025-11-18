# Mentoria-edu - Plataforma de dados

## Sumário

- [Descrição](##Descrição)
- [Estrutura](##Estrutura)
- [Get Started](##Get_started)
  - [Volumes](###Estrutura-de-Volumes-e-Desenvolvimento)
  - [Execução de Pipelines](###Exemplo-de-Uso-Prático)
  - [Exemplo de Uso Prático](###Exemplo-de-Uso-Prático)
- [Documentação](##Documentação)
- [Créditos](##Créditos)

## Descrição

Plataforma de **Data Lakehouse** desenvolvida para atuar como um **Data Bureau**, capaz de processar e gerenciar dados de qualquer domínio.
 A stack completa é orquestrada através de Docker Compose, containerizando todos os componentes: Spark para processamento, HDFS para armazenamento, Hive Metastore para catalogação de metadados. Esta abordagem garante consistência entre ambientes e facilita o deployment e escalabilidade da plataforma.

 Este pipeline segue a arquitetura "medallion" (bronze-silver-gold) com a adição da camada raw, garantindo qualidade crescente dos dados em cada camada e rastreabilidade completa desde os dados brutos até os modelos finais, com qualidade e performance otimizadas para análises de grandes volumes de dados.

---

> **Data Bureau** (ou "Escritório de Dados") é uma empresa ou organização que atua como um **repositório central e agregador de dados**. Ele coleta, compila, analisa e fornece informações detalhadas sobre indivíduos e empresas, principalmente para auxiliar outras organizações na **tomada de decisões**, especialmente relacionadas a **risco de crédito**, **conformidade** e **marketing**.
>

## Estrutura

```
plataforma_dados/
├── docs
├── hadoop_platform/                                    # Raiz da plataforma Hadoop
│        ├── compose/
│        │      └── docker-compose.yaml                 # Orquestração de containers
│        │
│        ├── configs/                                   # Diretorio raiz configurações dos serviços
│        │      ├── nodes/
│        │      │     ├── master_node/                  # Scripts de inicialização dos serviços
│        │      │     │       ├── start_hdfs.sh
│        │      │     │       ├── start_hive.sh
│        │      │     │       └── start_yarn.sh
│        │      │     │
│        │      │     └── worker_node/
│        │      │             └── worker_entrypoint.sh
│        │      │
│        │      └── services/                           # Configurações de cada serviço
│        │              ├── hadoop/
│        │              │     └── core-site.xml
│        │              ├── hdfs/
│        │              │     └── hdfs-site.xml
│        │              ├── hive/
│        │              │     └── hive-site.xml
│        │              ├── spark/
│        │              │     └── spark-defaults.config
│        │              └── yarn/
│        │                    ├── logs_yarn.sh            # Script de logs do YARN
│        │                    └── yarn-site.xml
│        │
│        ├── docker/
│        │      └── docker.Dockerfile                     # Dockerfile base da plataforma
│        │
│        └── scripts/                                   # Diretorio/volume clientnode
│               ├── exemplo1.py
│               └── exemplo2.py
│
├── CODEOWNERS.txt
├── README.md                                           # Documentação principal
└── start_platform.sh                                   # Script para iniciar a plataforma
```
## Get_started

Para iniciar a plataforma Data Lakehouse, execute o script de inicialização na raiz do projeto:

```bash
sudo ./start_platform.sh
```
Este comando irá:

- Inicializar todos os containers via Docker Compose
- Configurar os serviços: Masternode, Worker, PostgreSQL (Hive Metastore) e Clientnode
- Estabelecer a rede entre os componentes
- Preparar o ambiente para execução de pipelines

### Estrutura de Volumes e Desenvolvimento

O container clientnode possui um volume mapeado que sincroniza a pasta local scripts/ com /opt/scripts/ dentro do container. Isso permite o desenvolvimento iterativo dos pipelines:

```
# Estrutura de diretórios
plataforma_dados/
├── scripts/           # Pasta local
│   ├── pipeline1.py
│   ├── pipeline2.py
│   └── ...
└── ...

# Dentro do container clientnode:
/opt/scripts/         # Pasta sincronizada
├── pipeline1.py
├── pipeline2.py
└── ...
```
### Exemplo de Uso Prático

1. Desenvolva seu script na pasta scripts/ local:

> scripts/meu_pipeline.py

```bash
from pyspark.sql import SparkSession

spark = SparkSession.builder \
	.appName("Meu Pipeline") \
	.enableHiveSupport() \
	.getOrCreate()

# Seu código Spark aqui
df = spark.sql("SELECT * FROM raw.tabela_exemplo")
df.show()
```

2. Execute o pipeline:

```bash
sudo docker exec clientnode bash -c "/opt/spark/bin/spark-submit /opt/scripts/meu_pipeline.py"
```

## Documentação

Se você está planejando contribuir ou apenas deseja saber mais sobre este projeto, leia nossa [documentation](https://www.notion.so/1c408c995dce8017827cf53f445a924d?v=1c408c995dce803eb025000cdbd98892&p=29908c995dce8021ad68f9924a4e221c&pm=s).

## Creditos

- [Leonardo Adelmo](https://github.com/Leo-Adelmo)
- [Luiz Vaz](https://github.com/luiz-vaz)
- [Phill Andrade](https://github.com/Phill-Andrade)
- [Eduardo Katsurayama](https://github.com/eduardoKatsurayama)