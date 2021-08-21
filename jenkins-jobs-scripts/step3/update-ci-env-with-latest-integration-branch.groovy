pipeline {
    agent {
        node 'master'
    }
    stages {
        stage('Clean up') {
            steps {
                cleanWs()
            }
        }
        stage('Initial setup') {
            steps {
                // manifest repo
                checkout([  
                  $class: 'GitSCM', 
                  branches: [[name: 'refs/heads/master']], 
                  doGenerateSubmoduleConfigurations: false, 
                  extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: "${REPO_NAME}"]], 
                  submoduleCfg: [], 
                  userRemoteConfigs: [[credentialsId: 'themarcelor-github-token', url: "https://github.com/uc-cdis/${REPO_NAME}"]]
                ])
                // gen3-release-utils
                checkout([  
                  $class: 'GitSCM', 
                  branches: [[name: '*/master']], 
                  doGenerateSubmoduleConfigurations: false, 
                  extensions: [[$class: 'RelativeTargetDirectory', relativeTargetDir: 'gen3-release-utils']], 
                  submoduleCfg: [], 
                  userRemoteConfigs: [[credentialsId: 'themarcelor-github-token', url: 'https://github.com/uc-cdis/gen3-release-utils']]
                ])
            }
        }
        stage('Update CI environment') {
            steps {
              withCredentials([string(credentialsId: 'themarcelor-github-token', variable: 'GITHUB_TOKEN')]) {
                dir("gen3-release-utils") {
                    sh '''
                      cd gen3release-sdk
                      poetry install
                      poetry run gen3release apply -v $INTEGRATION_BRANCH -e ${WORKSPACE}/${REPO_NAME}/${TARGET_ENVIRONMENT} -pr "${PR_TITLE} ${INTEGRATION_BRANCH} ${TARGET_ENVIRONMENT} $(date +%s)"
                    '''
                }
              }
            }
        }
    }
}
