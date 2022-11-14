
const modal = document.getElementById("myModal")
const modalNewMsgBtn = document.getElementById("newMsgLink")
const span = document.getElementsByClassName("close")[0];

modalNewMsgBtn.addEventListener("click", function(e){
    e.preventDefault()
    modal.style.display="block";
})

span.addEventListener("click", function() {
    modal.style.display="none";
})

window.addEventListener("click", function(e) {
    if (e.target == modal) {
        modal.style.display = "none";
    }
})

const messageInput = document.getElementById('new-message')

messageInput.addEventListener('keyup', function(e) {
    let max =280;
    let curr_char_count = messageInput.value.length
    let charLimit = document.getElementById('charcount')
    console.log(curr_char_count)
    console.log(max)
    if (curr_char_count >= 260) {
        charLimit.innerText=`Character Limit: ${curr_char_count} / ${max}`
    } else {
        charLimit.innerText=""
    }
   
})
