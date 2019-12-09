$(document).ready(function () {

    $('table').DataTable(); //display..


    var product_id;
     //get product_id for the button clicked.
    $("button.delete_product").on("click", get_id);
    $("button.update_product").on("click",get_id);

    function get_id()
    {
        product_id = $(this).parent().parent().attr("id"); //get row id...

    }

    //
    $('#select_picker').change(function() {
    // $(this).val() will work here
        alert(this.value);


    });

    //async to delete product from database..

    $("#confirm_delete").on("click", function()
    {
         //send to flask using AJAX to delete_product from database.
        $.ajax({

            type: "POST",
            url: "/manage_product",
            data: { product_id: product_id, flag:"DELETE"},

            success: function(data)
            {
            if (data)
                {
                 //remove table row

                $("tr#" + product_id).remove();

                //remove from select ...

                //think about escaping characters to get it to work..
                  var product = data.del_product;
                  $(`#select_picker option[value=${product}]`).remove();

                  $('.close').click();

                }
            },
            error:function(data)
            {
                alert("failed to contact server");

            },

            });

    });

     // form used to update product in database..

     $("form#update_product").submit(function(e)
     {
        e.preventDefault();
        //get updated quantity bags from user and now we submit form with jquery ajax.
        var quantity = $("#bag_quantity").val();
        $.ajax({

            type: "POST",
            url:"/manage_product",
            data:{product_id:product_id, quantity:quantity, flag:"UPDATE"},

            success:function(data){
               //update the row of the form...
                if(data)
                {
                    //now we update the table....
                    $("tr#" + product_id + " " + 'td:nth-child(3)').text(data.quantity);
                    $('.close').click();

                }

            },
            error:function(){

                alert("failed to contact server");
            },

        });

    });

});