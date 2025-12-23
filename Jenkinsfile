pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/yasminerahhaoui/Predictive-Real-Estate-Prices',
                    credentialsId: 'github-token-app'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest tests/'  // si tu as des tests Python
            }
        }

    }
}
