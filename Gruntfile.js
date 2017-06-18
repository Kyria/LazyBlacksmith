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
                    'lazyblacksmith/**/*.py',
                ]
            },
        },

        less: {
            options: {
                cleancss: true,
                compress: false,
                modifyVars: {
                    'icon-font-path': '"../fonts/"',
                    'fa-font-path': '"../fonts"',
                    'ui-image-dir': '"../css/jquery-ui-images"',
                }
            },
            themes: {
                files: {
                    'lazyblacksmith/static/css/theme-default.css': 'lazyblacksmith/static/less/theme-default/bootstrap.less',
                }
            }
        },

        concat: {
            bootstrap: {
                src: [
                    'lazyblacksmith/static/bootstrap/js/modal.js',
                    'lazyblacksmith/static/bootstrap/js/tooltip.js',
                    'lazyblacksmith/static/bootstrap/js/popover.js',
                    'lazyblacksmith/static/bootstrap/js/button.js',
                    'lazyblacksmith/static/bootstrap/js/collapse.js',
                    'lazyblacksmith/static/bootstrap/js/dropdown.js',
                    'lazyblacksmith/static/bootstrap/js/tab.js',
                    'lazyblacksmith/static/bootstrap/js/affix.js',
                    'lazyblacksmith/static/bootstrap/js/alert.js',
                    'lazyblacksmith/static/bootstrap/js/transition.js',
                ],
                dest: 'lazyblacksmith/static/js/bootstrap.js'
            },
            css: {
                src: [
                    'lazyblacksmith/static/css/theme-default.css',
                    'lazyblacksmith/static/css/animate.css',
                ],
                dest: 'lazyblacksmith/static/css/theme-default-combined.css'
            }
        },

        cssmin: {
            options: {
                sourceMap: true,
            },
            target: {
                files: {
                    'lazyblacksmith/static/css/theme-default-combined.min.css': ['lazyblacksmith/static/css/theme-default-combined.css']
                }
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
                    'lazyblacksmith/static/js/lb/*.js',
                    'lazyblacksmith/static/js/lb/*/*.js',
                ],
                dest: 'lazyblacksmith/static/js/lazybl-combined.min.js'
            }
        },
    });

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    // Default task(s).
    grunt.registerTask('default', ['less', 'concat', 'cssmin', 'uglify']);
};
