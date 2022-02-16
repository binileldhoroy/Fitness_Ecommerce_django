var updateBtn = document.getElementsByClassName('update-cart')
var makePayment = document.getElementsByClassName('make-payment')

for(i = 0; i < updateBtn.length; i++){
    updateBtn[i].addEventListener('click',function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        

        console.log('productId :', productId, 'Action:',action)

        console.log('user:',user)

        if(user != 'AnonymousUser'){
            updateUserOrder(productId,action)
        }
    })
}


function updateUserOrder(productId,action){
    console.log('sending data...')
    url = '/update-item/'
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFTOKEN':csrftoken
        },
        body:JSON.stringify({'productId':productId,'action':action})
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('data:',data)
        location.reload()
    })
}