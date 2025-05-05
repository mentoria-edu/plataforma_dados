    #!/bin/bash
    set -ex
    
    echo "Iniciando HDFS datanode..."
    hdfs --daemon start datanode 
    
    echo "Iniciando YARN nodemanager..."
    yarn nodemanager