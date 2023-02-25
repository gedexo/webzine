$.ajax({
    url: '/add-cart/',
    type:'POST',
    data:data,
    dataType: "json",
    cache: false,
    beforeSend: function() {
        $(thisProp).prop('disabled', true); // disable button
      },
    success: function(response){
        $("[id=cartCount]").html(response['length'])
        $(thisProp).prop('disabled', false);

        if(response['msg'] == '1'){
            $('#icon'+productId).toggleClass('fa-light fa-cart-arrow-down');
        }
        else{
            $('#icon'+productId).toggleClass('fa-light fa-cart-arrow-down');
        }
    }
});