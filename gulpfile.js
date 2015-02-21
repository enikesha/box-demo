var gulp = require('gulp');
var path = require('path');
var less = require('gulp-less');

var paths = {
  less: './main/static/less/*.less',
}

gulp.task('less', function() {
  gulp.src(paths.less)
    .pipe(less())
    .pipe(gulp.dest('./main/static/css/'));
});

gulp.task('js', function() {
  gulp.src('./bower_components/jquery/dist/jquery.min.*')
    .pipe(gulp.dest('./main/static/js/'));

  gulp.src('./bower_components/bootstrap/dist/js/bootstrap.min.js')
    .pipe(gulp.dest('./main/static/js/'));
});

gulp.task('fonts', function() {
  gulp.src('./bower_components/bootstrap/dist/fonts/*')
    .pipe(gulp.dest('./main/static/fonts/'));
});

gulp.task('build', ['less','js','fonts']);

gulp.task('watch', ['build'], function() {
  gulp.watch([paths.less], ['less']);
});
