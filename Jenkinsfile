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
        DOCKER_CREDS   = credentials('docker-hub-token') 
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
                script {
                    docker.withRegistry('https://docker.io', 'docker-hub-token') {
                    // Il login è già avvenuto con successo qui dentro
                    def myImage = docker.build("warius67/mia-app:${env.BUILD_NUMBER}")
                    myImage.push()
                    }
                }
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
