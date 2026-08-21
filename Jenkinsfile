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
        K8S_API_URL  = 'https://192.168.2.111:50037' 
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
        stage('Helm Deploy sul Mac') {
            // Diciamo a Jenkins di far girare questo specifico stage dentro un container con Helm e Kubectl già pronti
            agent {
                docker {
                    image 'dtzar/helm-kubectl:latest'
                    // Forziamo il container a usare la rete dell'host per raggiungere l'IP del tuo Mac
                    args '-u root --network host'
                }
            }
            steps {
                script {
                    withCredentials([string(credentialsId: "${env.K8S_TOKEN_ID}", variable: 'KUBETOKEN')]) {
                        // All'interno di questo container i comandi si lanciano senza percorso assoluto
                        sh """
                            # 1. Configura temporaneamente il cluster puntando al tuo Mac
                            kubectl config set-cluster minikube-mac --server=${env.K8S_API_URL} --insecure-skip-tls-verify=true
                            kubectl config set-credentials jenkins-sa --token=${KUBETOKEN}
                            kubectl config set-context mac-context --cluster=minikube-mac --user=jenkins-sa --namespace=${env.NAMESPACE}
                            kubectl config use-context mac-context

                            # 2. Verifica la connessione di rete verso il cluster del Mac
                            echo "Verifico connessione a Minikube sul Mac..."
                            kubectl cluster-info

                            # 3. Esegui il deploy con Helm
                            echo "Avvio Helm Upgrade/Install nel namespace ${env.NAMESPACE}..."
                            helm upgrade --install ${env.RELEASE_NAME} ${env.CHART_PATH} \
                                --namespace ${env.NAMESPACE} \
                                --create-namespace \
                                --kube-insecure-skip-tls-verify \
                                --set image.repository=${env.IMAGE_NAME} \
                                --set image.tag=${env.DOCKER_TAG} \
                                --wait
                        """
                    }
                }
            }
        }

    }
}
