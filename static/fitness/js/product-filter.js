$(document).ready(function () {
    $('#loader').hide()
    $('.filter-checkbox,#priceFilterBtn').on('click',function(){
        var filterObj = {};
        var minPrice=$('#maxPrice').attr('min');
		var maxPrice=$('#maxPrice').val();
		filterObj.minPrice=minPrice;
		filterObj.maxPrice=maxPrice;
        $('.filter-checkbox').each(function (index, element) { 
            var filterVal = $(this).val();
            var filterKey = $(this).data('filter');
            filterObj[filterKey] = Array.from(document.querySelectorAll('input[data-filter='+filterKey+']:checked')).map(function(e){
                return e.value;
            })
        });
        
        $.ajax({
            url: "filter/",
            data: filterObj,
            dataType: "json",
            success: function (response) {
                $('#filterproducts').html(response.data)
                console.log(response)
                $('.loader').hide()
            }
        });
    })

    // Filter Product According to the price
	$("#maxPrice").on('blur',function(){
		var min=$(this).attr('min');
		var max=$(this).attr('max');
		var value=$(this).val();
		console.log(value,min,max);
		if(value < parseInt(min) || value > parseInt(max)){
			alert('Values should be '+min+'-'+max);
			$(this).val(min);
			$(this).focus();
			$("#rangeInput").val(min);
			return false;
		}
	});
	// End

});


