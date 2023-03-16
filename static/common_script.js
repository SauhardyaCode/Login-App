//task one
if (window.history.replaceState){
    window.history.replaceState( null, null, window.location.href );
}

//task two
setInterval(timer, 1)
function timer(){
    if (window.location!= sessionStorage['curr_page']) {
        window.location.reload()
    }
    sessionStorage["curr_page"] = window.location
}