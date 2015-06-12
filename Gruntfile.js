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

        concat: {
            bootstrap: {
                src: [                    
                    'lazyblacksmith/static/js/bootstrap/modal.js',
                    'lazyblacksmith/static/js/bootstrap/tooltip.js',
                    'lazyblacksmith/static/js/bootstrap/popover.js',
                    'lazyblacksmith/static/js/bootstrap/button.js',
                    'lazyblacksmith/static/js/bootstrap/collapse.js',
                    'lazyblacksmith/static/js/bootstrap/dropdown.js',
                    'lazyblacksmith/static/js/bootstrap/tab.js',
                    'lazyblacksmith/static/js/bootstrap/affix.js',
                    'lazyblacksmith/static/js/bootstrap/alert.js',
                    'lazyblacksmith/static/js/bootstrap/carousel.js',
                    'lazyblacksmith/static/js/bootstrap/transition.js',
                    'lazyblacksmith/static/js/bootstrap/scrollspy.js',
                ],
                dest: 'lazyblacksmith/static/js/bootstrap.js'
            }
        },
        uglify: {
            combined: {
                options: {
                    sourceMap: true
                },
                src: [
                    'lazyblacksmith/static/js/bootstrap.js',
                    'lazyblacksmith/static/js/jquery/*.js',
                    'lazyblacksmith/static/js/misc/*.js',
                    'lazyblacksmith/static/js/lazyblacksmith.js',
                    'lazyblacksmith/static/js/lazyblacksmith.*.js',
                ],
                dest: 'lazyblacksmith/static/js/lazybl-combined.min.js'
            }
        },
        less: {
            options: {
                cleancss: true,
                compress: true,
                modifyVars: {
                    'icon-font-path': '"../fonts/"',
                    'fa-font-path': '"../fonts"',
                    'ui-image-dir': '"../css/jquery-ui-images"',
                }
            },
            themes: {
                files: {
                    'lazyblacksmith/static/css/theme-default.min.css': 'lazyblacksmith/static/less/theme-default/bootstrap.less',
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-flake8');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-less');

    // Default task(s).
    grunt.registerTask('default', ['concat', 'uglify', 'less']);

    grunt.loadNpmTasks('grunt-flake8');
};
