module.exports = function (grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        flake8: {
            options: {
                ignore: ['E501']
            },
            LazyBlacksmith_models: {
                src: [
                    'LazyBlacksmith/models/*.py',
                    'LazyBlacksmith/models/*/*.py',
                ]
            },
            LazyBlacksmith: {
                src: [
                    'lazyblacksmith/*.py',
                ]
            },
        },
    });

    grunt.loadNpmTasks('grunt-flake8');
};
