**Istruzioni**

*Connessioni*
Estrarre dal log di Kibana da questo link:
https://cometa-logging.prod.cluster.internal/app/r/s/pP5Kp
cometa.namespace: ask-stella
stringa di ricerca: "Websocket ws/"

Salvare il file nella cartella: ./input_folder con estensione .csv senza eliminare i file presenti.
I file presenti nella cartella verranno poi unificati in un file nella cartella ./input e chiamato **csv_unito.csv**

Eseguire lo script ***main_union.py***

Il file prodotto si trova nella cartella ./output con il nome **username_counts.csv**

*Domande*
Estrarre dal log di Kibana da questo link:
cometa.namespace: ask-stella
stringa di ricerca: 'cometa.log.message: "User Message"'

Salvare il file nella cartella ./input_folder_question con estensione .CSV senza eliminare i file presenti.

I file presenti nella cartella verranno poi unificati in un file nella cartella ./input con il nome di **lista_domande_unito.csv**

Eseguire lo script ***question_union.py***

Il file prodotto si trova nella cartella ./output con il nome **domande_estratte.csv**

