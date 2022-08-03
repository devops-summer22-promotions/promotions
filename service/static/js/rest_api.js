$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_name").val(res.name);
        $("#promotion_type").val(res.type);
        $("#promotion_discount").val(res.discount);
        $("#promotion_customer").val(res.customer);
        $("#promotion_start_date").val(res.start_date);
        $("#promotion_end_date").val(res.end_date);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_name").val("");
        $("#promotion_type").val("");
        $("#promotion_discount").val("");
        $("#promotion_customer").val("");
        $("#promotion_start_date").val("");
        $("#promotion_end_date").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#promotion_name").val();
        let type = $("#promotion_type").val();
        let discount = $("#promotion_discount").val();
        let customer = $("#promotion_customer").val();
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();

        let data = {
            "name": name,
            "type": type,
            "discount": discount,
            "customer": customer,
            "start_date": start_date,
            "end_date": end_date
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success, created a promotion")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {

        let promotion_id = $("#promotion_id").val()
        let name = $("#promotion_name").val();
        let type = $("#promotion_type").val();
        let discount = $("#promotion_discount").val();
        let customer = $("#promotion_customer").val();
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();

        let data = {
            "name": name,
            "type": type,
            "discount": discount,
            "customer": customer,
            "start_date": start_date,
            "end_date": end_date
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Success, updated a promotion")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success, retrieved a promotion")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Cancel a Promotion
    // ****************************************

    $("#cancel-btn").click(function () {
        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/promotions/${promotion_id}/cancel`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Success, promotion has been cancelled!")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Pet
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Success, promotion has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {

        let name = $("#promotion_name").val();
        let type = $("#promotion_type").val();
        let discount = $("#promotion_discount").val();
        let customer = $("#promotion_customer").val();
        let start_date = $("#promotion_start_date").val();
        let end_date = $("#promotion_end_date").val();

        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }

        if (type) {
            if (queryString.length > 0) {
                queryString += '&type=' + type
            } else {
                queryString += 'type=' + type
            }
        }

        if (discount) {
            if (queryString.length > 0) {
                queryString += '&discount=' + discount
            } else {
                queryString += 'discount=' + discount
            }
        }

        if (customer) {
            if (queryString.length > 0) {
                queryString += '&customer=' + customer
            } else {
                queryString += 'customer=' + customer
            }
        }

        if (start_date) {
            if (queryString.length > 0) {
                queryString += '&start_date=' + start_date
            } else {
                queryString += 'start_date=' + start_date
            }
        }

        if (end_date) {
            if (queryString.length > 0) {
                queryString += '&end_date=' + end_date
            } else {
                queryString += 'end_date=' + end_date
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Type</th>'
            table += '<th class="col-md-1">Discount</th>'
            table += '<th class="col-md-1">Customer</th>'
            table += '<th class="col-md-2">Start Date</th>'
            table += '<th class="col-md-2">End Date</th>'
            table += '</tr></thead><tbody>'
            let firstpromo = "";
            for (let i = 0; i < res.length; i++) {
                let promo = res[i];
                table += `<tr id="row_${i}"><td>${promo.id}</td><td>${promo.name}</td><td>${promo.type}</td><td>${promo.discount}</td><td>${promo.customer}</td><td>${promo.start_date}</td><td>${promo.end_date}</td></tr>`;
                if (i == 0) {
                    firstpromo = promo;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstpromo != "") {
                update_form_data(firstpromo)
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // clear the selected type so that search can return all promotions
    clear_form_data();

})
