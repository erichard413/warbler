
const btns = document.querySelectorAll('.btn')

btns.forEach(function (e) {
    e.addEventListener('click', async function(e){
        e.preventDefault()
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

