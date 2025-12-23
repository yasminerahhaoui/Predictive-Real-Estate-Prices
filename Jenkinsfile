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
                bat '''
                python -m venv .venv
                call .venv\\Scripts\\activate
                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                bat '''
                call .venv\\Scripts\\activate
                pytest test_app.py -v
                '''
            }
        }
    }
}
