'use strict';

module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    // Metadata.
    pkg: grunt.file.readJSON('package.json'),
    banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
      '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
      '<%= pkg.homepage ? "* " + pkg.homepage + "\\n" : "" %>' +
      '* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author.name %>;' +
      ' Licensed <%= _.pluck(pkg.licenses, "type").join(", ") %> */\n',
    // Task configuration.
    concat: {
      options: {
        banner: '<%= banner %>',
        stripBanners: true
      },
      dist: {
        src: ['pub/js/**/*.js'],
        dest: 'pub/<%= pkg.name %>.js'
      },
    },
    uglify: {
      options: {
        banner: '<%= banner %>'
      },
      dist: {
        src: '<%= concat.dist.dest %>',
        dest: 'pub/<%= pkg.name %>.min.js'
      },
    },
   requirejs: {
     // global config
     options: {
       baseUrl: "pub/js/",
       mainConfigFile: "common/config.js"
     },
     production: {
       // overwrites the default config above
       options: {
         out: "common/production.js"
       }
     },
     development: {
       // overwrites the default config above
       options: {
         out: "common/development.js",
         optimize: '' // no minification
       }
     }
   },
    //nodeunit: {
      //files: ['test/**/*_test.js']
    //},
    jshint: {
      options: {
        jshintrc: '.jshintrc'
      },
      gruntfile: {
        src: 'Gruntfile.js'
      },
      //pub: {
        //options: {
          //jshintrc: 'static/js/.jshintrc'
        //},
        //src: ['pub/js/**/*.js']
      //},
      //test: {
        //src: ['test/**/*.js']
      //},
    },
   coffee: {
     compile: {
         //files: grunt.file.expandMapping(['static/js/**/*.coffee'],'public/js/',{
         //rename: function(destBase,destPath) {
            //console.log(destBase);
            //console.log(destPath);
           //return destBase+destPath.replace(/\.coffee$/,".js");
         //}
         files: [
                 {
                   expand: true,     // Enable dynamic expansion.
                   cwd: 'static/js/',      // Src matches are relative to this path.
                   src: ['**/*.coffee'], // Actual pattern(s) to match.
                   dest: 'pub/js',   // Destination path prefix.
                   ext: '.js',   // Dest filepaths will have this extension.
                 },
               ],
         }
   },
    watch: {
      gruntfile: {
        files: '<%= jshint.gruntfile.src %>',
        tasks: ['jshint:gruntfile']
      },
      //pubJs: {
        //files: '<%= jshint.pub.src %>',
        //tasks: ['jshint:pub', 'nodeunit']
      //},
      //test: {
        //files: '<%= jshint.test.src %>',
        //tasks: ['jshint:test', 'nodeunit']
      //},
      coffee:{
         files:['static/js/*.coffee'],
         tasks:'coffee:compile'
      },
    },
  });

  // These plugins provide necessary tasks.
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-nodeunit');
  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-coffee');
  grunt.loadNpmTasks('grunt-contrib-requirejs');

  // Default task.
  //grunt.registerTask('default', ['jshint', 'nodeunit', 'concat', 'uglify', 'coffee']);
  grunt.registerTask('default', ['jshint', 'concat', 'uglify', 'coffee']);
  grunt.registerTask('test-requireJs-production', 'requirejs:production');

};
