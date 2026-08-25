pipeline {
    agent {
        // Dice a Jenkins di non creare Pod, ma di usare l'agente fisico con questa label
        label 'mac-agent'
    }
    environment {
        IMAGE_NAME     = 'warius67/flask-app-example-build'
        NAMESPACE      = 'formazione-sou'
        RELEASE_NAME   = 'flask-app'
        CHART_PATH     = 'charts/flask-app'
        DOCKER_CREDS   = credentials('token-docker-hub') 
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
        stage('Docker Build & Push') {
            steps {
                // Esegue i comandi direttamente sulla macchina, usando il Docker reale
                sh """
                    echo "\$DOCKER_CREDS" | docker login -u "warius67" --password-stdin
                    
                    docker build -t ${env.IMAGE_NAME}:${env.DOCKER_TAG} -f Dockerfile .
                    docker push ${env.IMAGE_NAME}:${env.DOCKER_TAG}
                    
                    if [ "${env.PUSH_LATEST}" = "true" ]; then
                        docker tag ${env.IMAGE_NAME}:${env.DOCKER_TAG} ${env.IMAGE_NAME}:latest
                        docker push ${env.IMAGE_NAME}:latest
                    fi
                """
            }
        }
        stage('Helm Deploy') {
            steps {
                // Esegue il deploy usando helm e il contesto kubectl della macchina ospitante
                sh """
                    echo "Eseguo il deploy tramite l'Helm installato sulla macchina..."
                    
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
