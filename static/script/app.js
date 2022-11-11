
const btns = document.querySelectorAll('.btn')

btns.forEach(function (e) {
    e.addEventListener('click', async function(e){
        messageId = (e.target.id).toString()
        await axios.post(`/users/add_like/${messageId}`)
        
        let btn = (e.target.closest("button"))
        if (btn.classList.contains('btn-primary')) {
            btn.classList.remove('btn-primary')
            btn.classList.add('btn-secondary')
        }
        else {
            btn.classList.remove('btn-secondary')
            btn.classList.add('btn-primary')
        }
        
    })
})

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

// function char_limit(messageInput) {
//     let max_chars = 279;
//     if (messageInput.value.length > max_chars) {
//         messageInput.value = messageInput.value.slice(0, max_chars)
//     }
// }
// messageInput.addEventListener('keydown', function(e) {
//     char_limit(messageInput)
// })