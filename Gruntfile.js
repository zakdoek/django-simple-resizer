/**
 * A gruntfile that provides in some automatisation of python development.
 */
module.exports = function( grunt ) {
    
    "use strict";

    grunt.initConfig({

        // Lint the files
        pylint: {
            options: {
                rcfile: ".pylintrc",
                virtualenv: "venv",
                externalPylint: true
            },

            src_package: {
                src: [
                    "simple_resizer"
                ]
            }
        },

        // Grunt shell
        shell: {
            options: {
                stdout: true,
                failOnError: true
            },
            pep8_package: {
                command: "pep8 simple_resizer --exclude=_version.py"
            },

            testrunner: {
                command: "./testrunner.py"
            }
        },

        // Watch for changes and test again
        watch: {
            src_package: {
                files: "resizer/**/*.py",
                tasks: [ "shell:pep8_package", "pylint:src_package",
                         "shell:testrunner" ]
            },

            gruntfile: {
                files: "./Gruntfile.js",
                tasks: [ "default" ]
            }
        }
    });

    grunt.loadNpmTasks( "grunt-pylint" );
    grunt.loadNpmTasks( "grunt-contrib-watch" );
    grunt.loadNpmTasks( "grunt-shell" );

    grunt.registerTask( "develop", [ "shell:pep8_package", "pylint", "shell:testrunner", "watch" ] );
    grunt.registerTask( "default", [ "shell:pep8_package", "pylint", "shell:testrunner" ] );
};
