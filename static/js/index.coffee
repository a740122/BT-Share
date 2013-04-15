# Require.js allows us to configure shortcut alias
require.config
  # The shim config allows us to configure dependencies for
  # scripts that do not call define() to register a module
    shim:
      "bootstrap":
        deps:['jquery'],
        exports: "$.fn.popover"
    paths:
      jquery: 'lib/jquery',
      bootstrap:'lib/bootstrap'


# Start the main app logic.
requirejs ['jquery', 'bootstrap'],($,bootstrap) ->
  $ ->
    $('#search-form').submit ->
      keyWord = $("#search-form input:first").val()
      redirectUrl = window.location.protocol+"//"+window.location.host+'/search/'
      if keyWord
        redirectUrl += "q_"+keyWord
      setTimeout (-> window.location = redirectUrl),1
      false