def buildAndPushTag(Map args) {
    def defaults = [
        registryUrl: '',
        credentialsId: 'docker-hub-token',
        dockerfileDir: "./",
        dockerfileName: "Dockerfile",
        buildArgs: "",
        pushLatest: true
    ]
    
    args = defaults + args

    docker.withRegistry(args.registryUrl, args.credentialsId) {
        def image = docker.build(args.image, "${args.buildArgs} ${args.dockerfileDir} -f ${args.dockerfileName}")
        image.push(args.buildTag)
        if(args.pushLatest) {
            image.push("latest")
            sh "docker rmi --force ${args.image}:latest"
        }
        sh "docker rmi --force ${args.image}:${args.buildTag}"

        return "${args.image}:${args.buildTag}"
    }
}

pipeline {
    agent { label 'rocky-linux-worker' }
    environment {
        IMAGE_NAME   = 'warius67/flask-app-example-build'
        
        // --- NUOVE VARIABILI PER IL CLUSTER SUL MAC ---
        K8S_TOKEN_ID = 'k8s-mac-token'
        K8S_API_URL = 'https://localhost:50877'
        NAMESPACE    = 'formazione-sou'
        RELEASE_NAME = 'flask-app'
        CHART_PATH   = 'charts/flask-app'
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
                    // Nota: rimosse le virgolette intorno a env.PUSH_LATEST per passarlo come booleano nativo
                    def pushLatestBool = env.PUSH_LATEST.toBoolean()
                    def pushedImage = buildAndPushTag(
                        image: "${env.IMAGE_NAME}",
                        buildTag: "${env.DOCKER_TAG}",
                        pushLatest: pushLatestBool
                    ) 
                    echo "Successo! Immagine pushata: ${pushedImage}" 
                }
            }
        }
        stage('Helm Deploy via SSH Tunnel') {
            agent {
                docker {
                    image 'alpine/helm:latest'
                    args '-u root --network host --entrypoint=""'
                }
            }
            steps {
                script {
                    // Assicurati di avere le credenziali SSH del tuo Mac salvate su Jenkins
                    withCredentials([string(credentialsId: "${env.K8S_TOKEN_ID}", variable: 'KUBETOKEN')]) {
                        sh '''
                            # Installa il client SSH nel container se mancante
                            apk add --no-cache openssh-client

                            # Crea un tunnel SSH in background: mappa la porta del Mac sulla VM dell'agent
                            # Sostituisci 'utente_mac' con il tuo nome utente del Mac
                            ssh -o StrictHostKeyChecking=no -N -L 50877:127.0.0.1:50877 utente_mac@192.168.7.1 &
                            TUNNEL_PID=$!
                            sleep 2 # Attendi che il tunnel si stabilizzi

                            # 1. Configura temporaneamente il cluster puntando a localhost (grazie al tunnel)
                            kubectl config set-cluster minikube-mac --server=${K8S_API_URL} --insecure-skip-tls-verify=true
                            kubectl config set-credentials jenkins-sa --token=${KUBETOKEN}
                            kubectl config set-context mac-context --cluster=minikube-mac --user=jenkins-sa --namespace=${NAMESPACE}
                            kubectl config use-context mac-context

                            # 2. Verifica la connessione
                            kubectl cluster-info

                            # 3. Esegui il deploy con Helm
                            helm upgrade --install ${RELEASE_NAME} ${CHART_PATH} \
                                --namespace ${NAMESPACE} \
                                --create-namespace \
                                --kube-insecure-skip-tls-verify \
                                --set image.repository=${IMAGE_NAME} \
                                --set image.tag=${DOCKER_TAG} \
                                --wait

                            # Chiudi il tunnel SSH al termine
                            kill $TUNNEL_PID
                        '''
                    }
                }
            }
        }
    }
}
