setInterval(timer, 1)

function timer(){
    if (window.location!= sessionStorage['curr_page']) {
        window.location.reload()
    }
    sessionStorage["curr_page"] = window.location
}