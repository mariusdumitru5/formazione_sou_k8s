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
        IMAGE_NAME = 'warius67/flask-app-example-build'
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
                        env.DOCKER_TAG = 'build-${env.BUILD_NUMBER}'
                        env.PUSH_LATEST = 'false'
                    }
                }
            }
        }
        stage('Build and Push docker image') {
            steps {
                script {
                    def pushedImage = buildAndPushTag(
                        image: "${env.IMAGE_NAME}",
                        buildTag: "${env.DOCKER_TAG}"
                        pushLatest: "${env.PUSH_LATEST}"
                    ) 
                    echo "Successo! Immagine pushata: ${pushedImage}" 
                }
            }
        } 		
    }
}

