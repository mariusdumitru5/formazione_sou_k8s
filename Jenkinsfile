def buildAndPushTag(Map args) {
    def defaults = [
        registryUrl: 'https://docker.io',
	credentialsId: 'b05d2eff-9df6-4540-99d2-82913d680ccd'
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
	agent any
        environment {
		IMAGE_NAME = 'warius67/flask-app'
	}
	stages {
        	stage('Checkout') {
            		steps {
                		checkout scm // Lo esegui manualmente qui
            		}
        	}
		stage('Build and Push docker image') {
			steps {
				script {
					def pushedImage = buildAndPushTag (
					image: "${IMAGE_NAME}",
					buildTag: "${BUILD_NUMBER}"
				)  

				}
			}
		} 		
	} 
}
