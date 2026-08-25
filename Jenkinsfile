pipeline {
    agent { label 'Mac-cluster' }
    
    environment {
        IMAGE_NAME      = 'warius67/flask-app-example-build'
        HELM_RELEASE    = 'flask-app'
        HELM_CHART_DIR  = './charts/flask-app'
        KUBE_NAMESPACE  = 'default'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Tag Logic') {
            steps {
                script {
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
        
        stage('Build and Push docker image') {
            steps {
                script {
                    // Utilizza le credenziali di Jenkins tramite variabili d'ambiente fornite alla shell
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-token', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
                        sh """
                            echo "Eseguo il login su Docker Hub..."
                            echo "\$DOCKER_TOKEN" | docker login -u "\$DOCKER_USER" --password-stdin
                            
                            echo "Avvio la compilazione dell'immagine..."
                            docker build -t ${env.IMAGE_NAME}:${env.DOCKER_TAG} . -f Dockerfile
                            
                            echo "Eseguo il push dell'immagine..."
                            docker push ${env.IMAGE_NAME}:${env.DOCKER_TAG}
                        """
                        
                        if (env.PUSH_LATEST == 'true' && env.DOCKER_TAG != 'latest') {
                            sh """
                                docker tag ${env.IMAGE_NAME}:${env.DOCKER_TAG} ${env.IMAGE_NAME}:latest
                                docker push ${env.IMAGE_NAME}:latest
                                docker rmi --force ${env.IMAGE_NAME}:latest
                            """
                        }
                        
                        // Pulizia finale delle immagini locali per non riempire il Mac
                        sh "docker rmi --force ${env.IMAGE_NAME}:${env.DOCKER_TAG}"
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes via Helm') {
            steps {
                // Utilizza il file Kubeconfig configurato su Jenkins
                withCredentials([file(credentialsId: 'kubernetes-kubeconfig', variable: 'KUBECONFIG')]) {
                    sh """
                        echo "Inizio il deployment su Kubernetes tramite Helm..."
                        
                        helm upgrade --install ${env.HELM_RELEASE} ${env.HELM_CHART_DIR} \
                          --namespace ${env.KUBE_NAMESPACE} \
                          --set image.repository=${env.IMAGE_NAME} \
                          --set image.tag=${env.DOCKER_TAG} \
                          --atomic \
                          --timeout 5m
                          
                        echo "Deployment completato con successo!"
                    """
                }
            }
        }
    }
}