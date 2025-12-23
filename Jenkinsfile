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
        stage('Setup venv') {
            steps {
                bat """
                python -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                python -m pip install pytest
                """
            }
        }
        stage('Test') {
            steps {
                bat """
                call .venv\\Scripts\\activate
                python -m pytest test_app.py
                """
            }
        }
    }
}




