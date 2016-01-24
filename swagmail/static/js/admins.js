// Creates a new administrator via the API
function newAdmin(email, password, name) {

    $.ajax({
        url: '/api/v1/admins',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'email': email,
            'password': password,
            'name': name
        }),

        success: function (data) {
            addStatusMessage('success', 'The administrator was added successfully');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


// Deletes an administrator via the API
function deleteAdmin (id) {

    $.ajax({
        url: '/api/v1/admins/' + id,
        type: 'delete',

        success: function (data) {
            addStatusMessage('success', 'The administrator was successfully removed');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


// Sets the event listeners in the dynamic table
function adminEventListeners () {

    var adminEmail = $('a.adminEmail');
    var adminPassword = $('a.adminPassword');
    var adminName = $('a.adminName');
    var deleteModal = $('#deleteModal');
    var deleteModalBtn = $('#modalDeleteBtn');
    var newItemAnchor = $('#newItemAnchor');
    adminEmail.unbind();
    adminPassword.unbind();
    adminName.unbind();
    adminEmail.tooltip();
    adminPassword.tooltip();
    adminName.tooltip();

    adminPassword.editable({
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
            $(this).html('●●●●●●●●');
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s password was changed successfully');
        }
    });

    adminEmail.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'email': params.value })
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s email was changed successfully');
        }
    });

    adminPassword.editable({
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
            $(this).html('●●●●●●●●');
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s password was changed successfully');
        }
    });

    adminName.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'name': params.value })
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s name was changed successfully');
        }
    });

    deleteModal.unbind('show.bs.modal');
    deleteModal.on('show.bs.modal', function (e) {
        deleteModalBtn.attr('data-pk', $(e.relatedTarget).data('pk'));
    });

    deleteModalBtn.unbind('click');
    deleteModalBtn.on('click', function (e) {
        deleteModal.modal('hide');
        deleteAdmin($(this).attr('data-pk'));
    });

    // When the Add button is clicked, it will POST to the API
    newItemAnchor.unbind();
    newItemAnchor.on('click', function (e) {

        // Close any status messages
        $('#statusMessage div.alert button').trigger('click');

        var adminInput = $('#newAdminInput');
        var adminPasswordInput = $('#newAdminPasswordInput');
        var adminNameInput = $('#newAdminNameInput');

        // If adminInput is empty, highlight it in red
        if (!adminInput.val()) {
            adminInput.parent().addClass('has-error');
            adminInput.focus();
        }
            // If adminPasswordInput is empty, highlight it in red
        else if (!adminPasswordInput.val()) {
            adminPasswordInput.parent().addClass('has-error');
            adminPasswordInput.focus();
        }
            // If adminNameInput is empty, highlight it in red
        else if (!adminNameInput.val()) {
            adminNameInput.parent().addClass('has-error');
            adminNameInput.focus();
        }
        else {
            // Remove any error bordering on the input fields
            adminInput.parent().removeClass('has-error');
            adminPasswordInput.parent().removeClass('has-error');
            adminNameInput.parent().removeClass('has-error');
            // Create the new user
            newAdmin(adminInput.val(), adminPasswordInput.val(), adminNameInput.val());
            adminInput.val('');
            adminPasswordInput.val('');
            adminNameInput.val('');
            $('#filterRow input').val('');
        }

        e.preventDefault();
    });

    $('#newAdminInput, #newAdminPasswordInput, #newAdminNameInput').unbind();
    // When the user clicks out of the errored input field, the red border disappears
    $('#newAdminInput, #newAdminPasswordInput, #newAdminNameInput').blur(function () {
        $('#newAdminInput').parent().removeClass('has-error');
        $('#newAdminPasswordInput').parent().removeClass('has-error');
        $('#newAdminNameInput').parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    $('#newAdminInput, #newAdminPasswordInput, #newAdminNameInput').keyup(function (e) {
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
    apiURL = getApiUrl('admins');

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-title="Email: "><a href="#" class="adminEmail" data-pk="' + item.id + '" data-url="/api/v1/admins/' + item.id + '" title="Click to change the email">' + item.email + '</a></td>\
                    <td data-title="Password: "><a href="#" class="adminPassword" data-pk="' + item.id + '" data-url="/api/v1/admins/' + item.id + '" title="Click to change the password">●●●●●●●●</a></td>\
                    <td data-title="Name: "><a href="#" class="adminName" data-pk="' + item.id + '" data-url="/api/v1/admins/' + item.id + '" title="Click to change the name">' + item.name + '</a></td>\
                    <td data-title="Action: "><a href="#" class="deleteAnchor" data-pk="' + item.id + '" data-toggle="modal" data-target="#deleteModal">Delete</a></td>';
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? $('#addItemRow').before(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages']
        setPagination(result['meta']['page'], pages, 'admins');
        //Activate x-editable on new elements and other events
        adminEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {

        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('admins');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Populate the table
    fillInTable();

    // When hitting the back/forward buttons, reload the table
    $(window).bind("popstate", function () {
        fillInTable();
    });

    // Set the filter event listener
    var typeWatchOptions = {
        callback: function () { fillInTable() },
        wait: 750,
        captureLength: 2
    }

    $('#filterRow input').typeWatch(typeWatchOptions);
});
