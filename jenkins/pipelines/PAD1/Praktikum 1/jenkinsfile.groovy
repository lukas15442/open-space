node {
    stage('Build') {
        sh(
            '''
                chmod -Rf 777 ./
                rm -rf *
                cp -r "\\$(find \\$folder -maxdepth 1 -type d -not -path \\$folder/__pycache__ -not -path \\$folder)"/* ./
                rm -rf \f$folder
                clang++ -O0 -g -Wall -Wextra -Weverything -o binary *.cpp
            '''
        )
        warnings(
                canComputeNew: false,
                canResolveRelativePaths: false,
                categoriesPattern: '',
                consoleParsers: [[parserName: 'Clang (LLVM based)']],
                defaultEncoding: '',
                excludePattern: '',
                healthy: '',
                includePattern: '',
                messagesPattern: '',
                unHealthy: ''
        )
    }
    stage('Run valgrind') {
        runValgrind(
                childSilentAfterFork: false,
                excludePattern: '',
                generateSuppressions: false,
                ignoreExitCode: false,
                includePattern: 'binary',
                outputDirectory: '',
                outputFileEnding: '.valgrindReport',
                programOptions: '',
                removeOldReports: false,
                suppressionFiles: '',
                tool: [$class              : 'ValgrindToolMemcheck',
                       leakCheckLevel      : 'full',
                       showReachable       : true,
                       trackOrigins        : true,
                       undefinedValueErrors: true],
                traceChildren: false,
                valgrindExecutable: '',
                algrindOptions: '',
                workingDirectory: ''
        )
        publishValgrind(
                failBuildOnInvalidReports: false,
                failBuildOnMissingReports: false,
                failThresholdDefinitelyLost: '',
                failThresholdInvalidReadWrite: '',
                failThresholdTotal: '',
                pattern: '*valgrindReport',
                publishResultsForAbortedBuilds: false,
                publishResultsForFailedBuilds: false,
                sourceSubstitutionPaths: '',
                unstableThresholdDefinitelyLost: '0',
                unstableThresholdInvalidReadWrite: '0',
                unstableThresholdTotal: '0'
        )
    }
}