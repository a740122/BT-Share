define ['jquery','bootstrap'],($)->
  {
    bindSearch:->
      $('#search-form').submit ->
        keyWord = $("#search-form input:first").val()
        redirectUrl = window.location.protocol+"//"+window.location.host+'/search/'
        if keyWord
          redirectUrl += "q_"+encodeURI(keyWord)
        setTimeout (-> window.location = redirectUrl),1
        false
  }