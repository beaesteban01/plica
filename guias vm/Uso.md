# Uso del entorno
1. Inicia la máquina
```
vagrant up
```
2. Abre la consola
```
vagrant ssh
```
3. Abre Jupyter
```
cd PLICA/
jupyter notebook
```
4. Accede a jupyter desde *http://localhost:8888/* y abre un terminal
5. Modifica el fichero kibana.yml para habilitar la visualización
   
```
cd /home/vagrant/kibana-7.9.1-linux-x86_64/
nano kibana.yml
```
   - Sustituye `#server.host: “localhost”` por `server.host: 0.0.0.0`

6. Modifica las direciones del fichero .py y del notebook de kafka
```
# StructuredStreamingAndElasticPrueba.py
APP_NAME = "SparkStreaming.py"
PREDICTION_TOPIC = "IDSPRUEBA"
PERIOD = 10
BROKERS = 'localhost:9092'
base_path = "."

# Envio datos Kafka.ipynb
kafka_topic = 'IDSPRUEBA'
if type(kafka_topic) == bytes:
    kafka_topic = kafka_topic.decode('utf-8')
producer = KafkaProducer(bootstrap_servers=['localhost:9092'],api_version=(0,10))
PREDICTION_TOPIC = kafka_topic
```
7. Modifica el fichero .py para habilitar que se envíen los datos por elasticsearch
```
only_predictions.writeStream.outputMode("append").format("org.elasticsearch.spark.sql").option("checkpointLocation",'/tmp/checkpoint').start("index-name-4/doc-type").awaitTermination()

#only_predictions.writeStream.outputMode("append").format("console").start().awaitTermination()


#query2.awaitTermination()
```
8. Lanza Zookeeper, Kafka, un consumidor y crea un topic de Kafka
```
cd /home/vagrant/kafka

# Servidor zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties
# Comprobar si zookeeper esta corriendo con sudo lsof -i :2181 y matar el proceso con kill -9 <PID> si es necesario

# Servidor kafka
bin/kafka-server-start.sh config/server.properties
## Si no levanta el servidor kafka, borrar y volver a levantar
# rm -rf /kafka/logs

# Creación del topic
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic IDSPRUEBA

# Comprobación de que se ha creado el topic
bin/kafka-topics.sh --list --zookeeper localhost:2181

# Creación del consumidor
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic IDSPRUEBA --from-beginning
```
9. Lanza elasticsearch
```
cd /home/vagrant/elasticsearch
bin/elasticsearch
```
   - Para comprobar que está levantado modifica en `elasticsearch.yml` y descomenta `network.host:0.0.0.0`
   - Accede desde **http://localhost:9200/**
10. Lanza Kibana
```
cd /home/vagrant/kibana-7.9.1-linux-x86_64/
bin/kibana
```
   - Accede desde **http://localhost:5601/**
11. Ejecuta el .py con Spark
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.1 StructuredStreamingAndElasticPrueba.py
```
# Problemas con Elasticsearch
1. Error *ElasticsearchIllegalStateException[Failed to obtain node lock, is the following location writable?: [/home/vagrant/elasticsearchdata/]*
```
ps aux | grep 'java'
kill -9 <PID>
```
2. Error *the default discovery settings are unsuitable for production use; at least one of [discovery.seed_hosts, discovery.seed_providers, cluster.initial_master_nodes] must be configured*</br>
Modificar en `elasticsearch.yml`
```
# at least 
discovery.seed_hosts : []
cluster.initial_master_nodes : []
```
3. Error *max virtual memory areas vm.max_map_count [65530] is too low, increase to at least [262144]*
```
sysctl -w vm.max_map_count=262144
```
