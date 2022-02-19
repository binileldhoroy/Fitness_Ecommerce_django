// var updateBtn = document.getElementsByClassName('update-cart')
// var makePayment = document.getElementsByClassName('make-payment')

// for(i = 0; i < updateBtn.length; i++){
//     updateBtn[i].addEventListener('click',function(){
//         var productId = this.dataset.product
//         var action = this.dataset.action
        

//         console.log('productId :', productId, 'Action:',action)

//         console.log('user:',user)

//         if(user != 'AnonymousUser'){
//             updateUserOrder(productId,action)
//         }
//     })
// }


// function updateUserOrder(productId,action){
//     console.log('sending data...')
//     url = '/update-item/'
//     fetch(url,{
//         method:'POST',
//         headers:{
//             'Content-Type':'application/json',
//             'X-CSRFTOKEN':csrftoken
//         },
//         body:JSON.stringify({'productId':productId,'action':action})
//     })

//     .then((response) => {
//         return response.json()
//     })

//     .then((data) => {
//         console.log('data:',data)
//         location.reload()
//     })
// }

$('.update-cart').on('click',function (e) {
var product = $(this).data('product')
var action = $(this).data('action')
console.log(product)
console.log(action)
alert('hy')
    $.ajax({
        type : 'POST',
        url : "{% url 'update-item' %}",
        data : {
            productId : product,
            action : action,
            csrfmiddlewaretoken : "{{ csrf_token }}"
        },
        dataType: 'json',
        success:function(response){
            alert('done')
        }
    });
});

// $(document).ready(function() {
//     $('.update-cart').on('click',function (e) {
//         e.preventdefault();
//     var product = $(this).data('product')
//     var action = $(this).data('action')
//     console.log(product)
//     console.log(action)
//         $.ajax({
//             type : 'POST',
//             url : 'update-item/',
//             data : {
//                 productId : product,
//                 action : action,
//                 csrfmiddlewaretoken : "{{ csrf_token }}"
//             },
//             dataType: 'json',
//             success:function(response){
//                 alert('done')
//             }
//         });
//     });
// });