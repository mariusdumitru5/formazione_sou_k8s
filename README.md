<h1 align="center"> Deploy app note  con Helm su K8S</h1>

### Creazione Dockerfile

Come prima cosa è stato creato un Dockerfile per l'app che permette di creare, modificare ed eliminare delle note. Il Dockerfile è diviso in due stage per sfruttare la cache di docker.

### Creazione di Helm Chart 

Grazie a Helm possiamo mettere tutto quello che serve per deployare l'app su un cluster k8s in un unico posto. Helm sfrutta i template per fare questo. 
Per deployare l'app è stato creato un `deployment.yaml`, un `service.yaml` e un `ingress.yaml`. 

### Jenkins e Jenkinsfile 

Per fare tutto in modo automatico è stato creato prima un server Jenkins detto `jenkins master`. In questo caso il jenkins master si trova in un container docker avviato su una macchina virtuale. Sono state esposte le porte `8080` e `50000`. 
Lo step successivo è quello di collegare jenkins al cluster k8s che si trova sulla macchina host. Un modo per fare questo è quello di rendere l'host(nel mio caso un Mac) un agent di jenkins. 

Per fare tutto in automatico, bisogna mettere al centro della repo un `Jenkinsfile`. Questo file contiene tutti le istruzioni per fare la build dell'imagine docker, pushare l'immagine docker sul registry docker-hub e poi fare il deploy tramite helm nel cluster k8s. 
