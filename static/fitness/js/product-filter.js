$(document).ready(function () {
    $('#loader').hide()
    $('.filter-checkbox').on('click',function(){
        var filterObj = {};
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
            beforesend:function(){
                $('.loader').show()
            },
            success: function (response) {
                $('#filterproducts').html(response.data)
                console.log(response)
                $('.loader').hide()
            }
        });
    })
});