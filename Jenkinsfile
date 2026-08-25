pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                metadata:
                  namespace: formazione-sou
                  labels:
                    jenkins: agent
                spec:
                  # Forza l'uso del ServiceAccount amministrativo che abbiamo creato
                  serviceAccountName: jenkins-agent-sa
                  containers:
                  # CONTAINER 1: Il motore Docker (DinD) per fare Build e Push
                  - name: docker
                    image: docker:24.0.7-dind
                    command: ['dockerd-entrypoint.sh'] # Avvia correttamente il demone Docker
                    tty: true
                    securityContext:
                      privileged: true # FONDAMENTALE: Permette a Docker di girare dentro Kubernetes
                    volumeMounts:
                    - name: dind-storage
                      mountPath: /var/lib/docker
                  # CONTAINER 2: Helm e Kubectl per fare il Deploy
                  - name: helm-k8s
                    image: alpine/helm:3.12.3 # Contiene SIA helm SIA kubectl
                    command: ['cat']
                    tty: true
                  volumes:
                  - name: dind-storage
                    emptyDir: {}
                '''
        }
    }
    environment {
        IMAGE_NAME     = 'warius67/flask-app-example-build'
        NAMESPACE      = 'formazione-sou'
        RELEASE_NAME   = 'flask-app'
        CHART_PATH     = 'charts/flask-app'
        // Carica il token di Docker Hub configurato nelle credenziali di Jenkins
        DOCKER_CREDS   = credentials('docker-hub-token') 
    }
    stages {
        stage('Checkout') {
            steps {
                // Scarica il codice sorgente dalla tua repository Git
                checkout scm
            }
        }
        stage('Tag Logic') {
            steps {
                script {
                    // Calcola il tag dell'immagine in base al branch o al tag Git
                    if (env.TAG_NAME) {
                        env.DOCKER_TAG = env.TAG_NAME
                        env.PUSH_LATEST = 'false'
                    }
                    else if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                        env.DOCKER_TAG = 'latest'
                        env.PUSH_LATEST = 'true'
                    }
                    else if (env.BRANCH_NAME == 'develop') {
                        def gitCommitSha = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                        env.DOCKER_TAG = "develop-${gitCommitSha}"
                        env.PUSH_LATEST = 'false'
                    }
                    else {
                        env.DOCKER_TAG = "build-${env.BUILD_NUMBER}"
                        env.PUSH_LATEST = 'false'
                    }
                }
            }
        }
        stage('Docker Build & Push') {
            steps {
                // Entra dentro il container con il motore Docker
                container('docker') {
                    sh """
                        # Attende 5 secondi per garantire l'avvio completo del demone Docker
                        sleep 5
                        
                        # Login su Docker Hub usando le credenziali d'ambiente caricate da Jenkins
                        echo "\$DOCKER_CREDS" | docker login -u "warius67" --password-stdin
                        
                        # Compila l'immagine leggendo il Dockerfile della repository
                        docker build -t ${env.IMAGE_NAME}:${env.DOCKER_TAG} -f Dockerfile .
                        
                        # Esegue il Push dell'immagine su Docker Hub
                        docker push ${env.IMAGE_NAME}:${env.DOCKER_TAG}
                        
                        # Se richiesto dalla logica dei tag, applica e pusha anche il tag 'latest'
                        if [ "${env.PUSH_LATEST}" = "true" ]; then
                            docker tag ${env.IMAGE_NAME}:${env.DOCKER_TAG} ${env.IMAGE_NAME}:latest
                            docker push ${env.IMAGE_NAME}:latest
                        fi
                    """
                }
            }
        }
        stage('Helm Deploy') {
            steps {
                // Cambia ambiente ed entra nel container con Helm e Kubectl
                container('helm-k8s') {
                    sh """
                        echo "Eseguo il deploy diretto nel cluster locale..."
                        
                        # Verifica la connessione al cluster (eredita i permessi di cluster-admin del Pod)
                        kubectl cluster-info
                        
                        # Esegue l'installazione o l'aggiornamento del tuo Chart Helm passando il nuovo tag
                        helm upgrade --install ${env.RELEASE_NAME} ${env.CHART_PATH} \
                            --namespace ${env.NAMESPACE} \
                            --set image.repository=${env.IMAGE_NAME} \
                            --set image.tag=${env.DOCKER_TAG} \
                            --create-namespace \
                            --wait
                    """
                }
            }
        }
    }
}
