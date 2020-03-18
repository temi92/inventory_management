$(document).ready(function () {



    $('#customer_tables').DataTable();
    $("#product_tables").DataTable();
    $("#view_order_tables").DataTable();


    var errorInForm = false;

    $("#start_date").hide();
    $("#end_date").hide();



     // get date ...

    $("#start_datepicker").datepicker({onSelect: function(dateText, inst) {
        // we need to send this date to back-end..
        // we need to send this date to back-end..

         var selectedDate = $(this).datepicker("getDate");
         if (selectedDate > new Date())
          {

               $("#start_date").show();
                errorInForm=true;

          }

          else
          {
                $("#start_date").hide();
                errorInForm = false;

          }

        /*
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
                for (var i=0; i < propertyNames.length; i++)
                {
                    v = propertyNames[i];

                    $("#product_tables tbody").append('<tr><td align="center">' + propertyNames[i] + '</td><td align="center">'+ data[v] + '</td><tr>');
                  }


            },

        });
        */

    }
    });



    $("#end_datepicker").datepicker({onSelect: function(dateText, inst) {

        // we need to send this date to back-end..

         var selectedDate = $(this).datepicker("getDate");
         if (selectedDate > new Date())
          {

               $("#end_date").show();
                errorInForm=true;

          }

          else
          {
                $("#end_date").hide();
                errorInForm = false;

          }


    }
    });


    //intercept form from submitting if error flag is true.

    $("#view_product").submit(function (e){
        if (errorInForm){
            e.preventDefault();

        }




    })





});