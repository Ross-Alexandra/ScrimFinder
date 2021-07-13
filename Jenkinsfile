pipeline {
  agent any
  environment {
    CI = 'true'
  }
  stages {
    stage('Build') {
      steps {
        echo "Installing package requirements:"
        sh '(cd $WORKSPACE/scrim-finder-app && npm install)'
        sh '(cd $WORKSPACE/scrim-finder-app && npm run build)'
      }
    }
    stage('Test') {
      steps {
        echo 'Test'
      }
    }
    stage('Cleanup') {
        steps {
            echo 'Cleanup'
        }
    }
    stage('Master-Deploy') {
      when {
        expression { env.BRANCH_NAME == 'main' }
      }
      steps {
        sh 'sshpass -p $SCRIM_SEARCH_PASSWORD rsync -avzP $WORKSPACE/ scrimsearch@$SERVER:$SCRIM_SEARCH_LOCATION/'
        sh 'sshpass -p $SCRIM_SEARCH_PASSWORD ssh -oStrictHostKeyChecking=no scrimsearch@$SERVER "(cd $SCRIM_SEARCH_LOCATION/ && docker-compose down)"'
        sh 'sshpass -p $SCRIM_SEARCH_PASSWORD ssh -oStrictHostKeyChecking=no scrimsearch@$SERVER "(cd $SCRIM_SEARCH_LOCATION/ && NASCBOT_TOKEN=$NASCBOT_TOKEN INTERPROCESSAUTHKEY=$INTERPROCESSAUTHKEY SCRIMFINDERDB=$SCRIMFINDERDB POSTGRESHOST=$POSTGRESHOST POSTGRESPORT=$POSTGRESPORT SCRIMFINDERUSER=$SCRIMFINDERUSER SCRIMFINDERPASS=$SCRIMFINDERPASS SCRIM_FINDER_ENVIRONMENT=$ENVIRONMENT  docker-compose up --build -d)"'
      }
    }
  }
}