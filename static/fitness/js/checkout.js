$(document).ready(function () {
    
    $('.razorpay').click(function (e) { 
        e.preventDefault();
        
        var address_id = $('input[name="adrress"]:checked').val();
        var payment = $('input[name="payment"]:checked').val();
        var token = $("[name='csrfmiddlewaretoken']").val();

        if( address_id == undefined){
            swal("Alert", "Select Adderss!", "error");
            return false;
        }
        else{

            $.ajax({
                method: "GET",
                url: "/razorpay-payment",
                success: function (response) {
                    console.log(response)
                    var options = {
                        "key": "rzp_test_kEoSfK4F37QHr9", // Enter the Key ID generated from the Dashboard
                        "amount": response.cart_total * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                        "currency": "INR",
                        "name": "Fitness Ecommerce",
                        "description": "Thanku for shopping with us",
                        "image": "https://example.com/your_logo",
                        // "order_id": response.cur_order, //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                        "handler": function (response){
                            data = {
                                'payment':payment,
                                'cur_address':address_id,
                                csrfmiddlewaretoken : token
                            }
                            $.ajax({
                                method: "POST",
                                url: "razorpay-complete/",
                                data: data,
                                success: function (responsea) {
                                    swal("Congratulation", responsea.status, "success").then((value) => {
                                        window.location.href = '/my-orders'
                                      });
                                }
                            });
                        },
                        "prefill": {
                            "name": response.full_name,
                            "email": response.email,
                            "contact": response.phone
                        },
                        "theme": {
                            "color": "#3399cc"
                        }
                    };
                    var rzp1 = new Razorpay(options);
                    // rzp1.on('payment.failed', function (response){
                    //         alert(response.error.code);
                    //         alert(response.error.description);
                    //         alert(response.error.source);
                    //         alert(response.error.step);
                    //         alert(response.error.reason);
                    //         alert(response.error.metadata.order_id);
                    //         alert(response.error.metadata.payment_id);
                    // });
                    rzp1.open();
                }
            });
            
        }


    });

});