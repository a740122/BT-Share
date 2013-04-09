define [], () ->
   ->
    input = document.createElement "button"
    input.innerText = "Super Cool Test Button!"
    input.setAttribute "id", "the-button"
    document.body.appendChild input