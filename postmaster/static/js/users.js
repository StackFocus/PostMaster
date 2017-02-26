// Creates a new user via the API
function newUser(email, password) {

    $.ajax({
        url: '/api/v1/users',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'email': email,
            'password': password
        }),

        success: function(response) {
            addStatusMessage('success', 'The user was added successfully');
            fillInTable();
        },

        error: function(response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });
}


// Deletes a user via the API
function deleteUser(id) {

    $.ajax({
        url: '/api/v1/users/' + id,
        type: 'delete',

        success: function (response) {
            addStatusMessage('success', 'The user was successfully removed');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });
}


// Sets the event listeners for x-editable
function editableUserEventListeners() {

    var userPassword = $('a.userPassword');
    userPassword.unbind();
    userPassword.tooltip();

    userPassword.editable({
        type: 'password',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({'password': params.value})
        },

        display: function () {
            $(this).text('●●●●●●●●');
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        },

        success: function () {
            addStatusMessage('success', 'The user\'s password was changed successfully');
        }
    });
}


// Sets the event listeners in the dynamic table
function userEventListeners() {

    var deleteModal = $('#deleteModal');
    var deleteModalBtn = $('#modalDeleteBtn');
    var newItemAnchor = $('#newItemAnchor');

    // When hitting the back/forward buttons, reload the table
    $(window).bind("popstate", function () {
        fillInTable();
    });

    // Set the filter event listener
    var typeWatchOptions = {
        callback: function () { fillInTable() },
        wait: 750,
        captureLength: 2
    };

    $('#filterRow input').typeWatch(typeWatchOptions);

    deleteModal.on('show.bs.modal', function (e) {
        deleteModalBtn.attr('data-pk', $(e.relatedTarget).data('pk'));
    });

    deleteModalBtn.on('click', function (e) {
        deleteModal.modal('hide');
        deleteUser($(this).attr('data-pk'));
    });

    // When the Add button is clicked, it will POST to the API
    newItemAnchor.on('click', function (e) {

        // Close any status messages
        $('#statusMessage div.alert button').trigger('click');

        var userInput = $('#newUserInput');
        var passwordInput = $('#newPasswordInput');

        // If userInput is empty, highlight it in red
        if (!userInput.val()) {
            userInput.parent().addClass('has-error');
            userInput.focus();
        }
        // If passwordInput is empty, highlight it in red
        else if (!passwordInput.val()) {
            passwordInput.parent().addClass('has-error');
            passwordInput.focus();
        }
        else {
            // Remove any error bordering on the input fields
            userInput.parent().removeClass('has-error');
            passwordInput.parent().removeClass('has-error');
            // Create the new user
            newUser(userInput.val(), passwordInput.val());
            userInput.val('');
            passwordInput.val('');
            $('#filterRow input').val('');
        }

        e.preventDefault();
    });

    var newUserInputs = $('#newUserInput, #newPasswordInput');
    // When the user clicks out of the errored input field, the red border disappears
    newUserInputs.blur(function () {
        $('#newUserInput').parent().removeClass('has-error');
        $('#newPasswordInput').parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    newUserInputs.keyup(function (e) {
        var key = e.which;
        if (key == 13) {
            $('#newItemAnchor').trigger('click');
        }
    });
}


// Loads the dynamic table and pagination
function fillInTable () {
    // Set the loading spinner
    manageSpinner(true);

    // If the page or filter was specified, get the appropriate API URL
    apiURL = getApiUrl('users');

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            // Query the existing table row
            var tableRow = $('#dynamicTableRow' + String(i));
            // Create a new table row to be inserted or replace the current one
            var newTableRow = $('<tr />', {'id': 'dynamicTableRow' + String(i)});
            var columnDataUrl = '/api/v1/users/' + item.id;
            var email_td = $('<td />', {'data-title': 'Email: '}).text(item.email);
            var password_td = $('<td />', {'data-title': 'Password: '}).append(
                $('<a />', {'href': '#', 'class': 'userPassword', 'data-pk': item.id, 'data-url': columnDataUrl,
                            'title': 'Click to change the password'}).text('●●●●●●●●')
            );
            var action_td = $('<td />', {'data-title': 'Action: '}).append(
                $('<a />', {'href': '#', 'class': 'deleteAnchor', 'data-pk': item.id, 'data-toggle': 'modal',
                            'data-target': '#deleteModal'}).text('Delete')
            );
            // Add the new columns to the new table row
            newTableRow.append(email_td).append(password_td).append(action_td);

            // If the table row exists, then replace it, otherwise insert it
            if (tableRow.length > 0) {
                tableRow.replaceWith(newTableRow);
            }
            else {
                insertTableRow(newTableRow);
            }

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages'];
        setPagination(result['meta']['page'], pages, 'users');
        //Activate x-editable on new elements
        editableUserEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        // Remove the loading spinner
        manageSpinner(false);
        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('users');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Sets the default event listeners
    userEventListeners();

    // Populate the table
    fillInTable();
});
