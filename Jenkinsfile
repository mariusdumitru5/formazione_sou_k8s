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
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                metadata:
                  namespace: formazione-sou
                spec:
                  containers:
                  - name: docker
                    image: docker:24.0.7-dind
                    command: ['cat']
                    tty: true
                    securityContext:
                      privileged: true
                  - name: helm-k8s
                    image: bitnami/kubectl:latest
                    command: ['cat']
                    tty: true
                '''
        }
    }
    environment {
        IMAGE_NAME   = 'warius67/flask-app-example-build'
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
        stage('Helm Deploy') {
            steps {
                // Questo stage gira dentro il container 'helm-k8s' del Pod sul tuo Mac
                container('helm-k8s') {
                    sh """
                        echo "Siamo già dentro il cluster del Mac! Eseguo il deploy diretto..."
                        
                        helm upgrade --install ${env.RELEASE_NAME} ${env.CHART_PATH} \
                            --namespace ${env.NAMESPACE} \
                            --set image.repository=${env.IMAGE_NAME} \
                            --set image.tag=${env.DOCKER_TAG} \
                            --wait
                    """
                }
            }
        }
    }
}
