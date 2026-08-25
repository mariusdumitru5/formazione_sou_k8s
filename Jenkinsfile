pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                metadata:
                  namespace: formazione-sou
                spec:
                  # Associa il ServiceAccount con permessi di Cluster-Admin creato prima
                  serviceAccountName: jenkins-agent-sa
                  containers:
                  # Container 1: Il motore Docker (DinD) per fare Build e Push
                  - name: docker
                    image: docker:24.0.7-dind
                    command: ['dockerd-entrypoint.sh'] # Avvia il demone Docker
                    tty: true
                    securityContext:
                      privileged: true # Necessario per far girare Docker dentro un container
                    volumeMounts:
                    - name: dind-storage
                      mountPath: /var/lib/docker
                  # Container 2: Helm e Kubectl per fare il Deploy sul cluster del Mac
                  - name: helm-k8s
                    image: alpine/helm:3.12.3 # Contiene sia l'eseguibile 'helm' che 'kubectl'
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
        // Carica le credenziali salvate su Jenkins (es. come Secret Text o Username/Password)
        DOCKER_CREDS   = credentials('docker-hub-token') 
    }
    stages {
        stage('Checkout') {
            steps {
                # Scarica il codice della tua repository Git
                checkout scm
            }
        }
        stage('Tag Logic') {
            steps {
                script {
                    # Calcola il tag dell'immagine in base al branch o al tag Git
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
                # Entriamo dentro il primo container (quello con Docker)
                container('docker') {
                    sh """
                        # Aspetta 5 secondi per dare il tempo al demone Docker di avviarsi sullo sfondo
                        sleep 5
                        
                        # Login su Docker Hub usando la variabile d'ambiente di Jenkins
                        echo "\$DOCKER_CREDS" | docker login -u "warius67" --password-stdin
                        
                        # Fai la build dell'immagine leggendo il Dockerfile della repo
                        docker build -t ${env.IMAGE_NAME}:${env.DOCKER_TAG} -f Dockerfile .
                        
                        # Push dell'immagine su Docker Hub
                        docker push ${env.IMAGE_NAME}:${env.DOCKER_TAG}
                        
                        # Se siamo su main/master, pusha anche il tag 'latest'
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
                # Usciamo da Docker ed entriamo nel secondo container (quello con Helm)
                container('helm-k8s') {
                    sh """
                        echo "Eseguo il deploy diretto nel cluster Kubernetes..."
                        
                        # Sfrutta il ServiceAccount del Pod per autenticarsi automaticamente nel cluster del Mac
                        kubectl cluster-info
                        
                        # Esegue l'upgrade o l'installazione del tuo Chart Helm passando il nuovo tag dell'immagine
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
