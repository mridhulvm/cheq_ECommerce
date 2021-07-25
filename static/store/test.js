$('#coupon').click(function(){
    var coupon=$('#coupon_title').val()
   
        $.ajax({
            url:"{% url 'checkCoupon' %}",
            method: 'GET',
            data: {'data':coupon},
            dataType: 'json',
            success: function (data) {
  
              console.log(data)
             
              
              
              if(data.status){
                $('#display_coupon').html(data.message)
              }
              else
              {
                  $('#grand_total').html(data.total)
              }
             
            },
            error: function(error){
              console.log("Ajax cant send data")
            }
        })
      })