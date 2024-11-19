pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Jrecos/SG19B01-INTEGRACION-CONTINUA.git'
            }
        }
        
        stage('Unit Test') {
            steps {
                echo 'This stage is to running unit test'
            }
        }
        
        stage('Code analysis') {
            steps {
                echo 'Thsi stage is to running the code analysis'
            }
        }
        
        stage('Deploy') {
            steps {
                bat '''
                docker-compose up -d --build
                '''
            }
        }
    }
}
