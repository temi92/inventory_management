$(document).ready(function () {



    $('#customer_tables').DataTable();





     // get date ...
     //this is for manage_product_1.html...

    $("#datepicker").datepicker({onSelect: function(dateText, inst) {
        // we need to send this date to back-end..

        $.ajax({

            type: "POST",
            url: "/view_product",
            data: { date:dateText},
            success:function(data){

                $('#product_tables').DataTable(
                );
                    //display..

                $("#product_tables tbody tr").remove();
                 //update table ...
                data = JSON.stringify(data);
                data = JSON.parse(data);
                var propertyNames = Object.keys(data);
                for (var i=0; i < propertyNames.length; i++){
                    v = propertyNames[i];

                    $("#product_tables tbody").append('<tr><td align="center">' + propertyNames[i] + '</td><td align="center">'+ data[v] + '</td><tr>');
                  }


            },



        });

    }
    });






});