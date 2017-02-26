// Creates a new administrator via the API
function newAdmin(username, password, name) {

    $.ajax({
        url: '/api/v1/admins',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'username': username,
            'password': password,
            'name': name
        }),

        success: function (response) {
            addStatusMessage('success', 'The administrator was added successfully');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });
}


// Deletes an administrator via the API
function deleteAdmin(id) {

    $.ajax({
        url: '/api/v1/admins/' + id,
        type: 'delete',

        success: function (response) {
            addStatusMessage('success', 'The administrator was successfully removed');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });
}

// Unlocks an administrator via the API
function unlockAdmin(id, targetLink) {

    $.ajax({
        url: '/api/v1/admins/' + id + '/unlock',
        type: 'put',

        success: function (response) {
            addStatusMessage('success', 'The administrator was unlocked successfully');
            targetLink.parent('td').html('Unlocked');
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });

}

// Sets the event listeners for x-editable
function editableAdminEventListeners() {

    var adminUsername = $('a.adminUsername');
    var adminPassword = $('a.adminPassword');
    var adminName = $('a.adminName');
    var adminLocked = $('a.adminLocked')

    adminUsername.unbind();
    adminPassword.unbind();
    adminName.unbind();
    adminLocked.unbind();
    adminUsername.tooltip();
    adminPassword.tooltip();
    adminName.tooltip();
    adminLocked.tooltip();

    adminUsername.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'username': params.value })
        },

        display: function (value) {
            $(this).html(filterText(value.toLowerCase()));
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s username was changed successfully');
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
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
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

        display: function (value) {
            $(this).html(filterText(value));
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        },

        success: function () {
            addStatusMessage('success', 'The administrator\'s name was changed successfully');
        }
    });

    adminLocked.on('click', function(e) {
        var target = $(e.target);
        unlockAdmin(target.attr('data-pk'), target);
        e.preventDefault();
    });
}

// Sets the event listeners in the dynamic table
function adminEventListeners () {

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
        deleteAdmin($(this).attr('data-pk'));
    });

    // When the Add button is clicked, it will POST to the API
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

    var newAdminInputs = $('#newAdminInput, #newAdminPasswordInput, #newAdminNameInput');
    // When the user clicks out of the errored input field, the red border disappears
    newAdminInputs.blur(function () {
        $('#newAdminInput').parent().removeClass('has-error');
        $('#newAdminPasswordInput').parent().removeClass('has-error');
        $('#newAdminNameInput').parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    newAdminInputs.keyup(function (e) {
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

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            // Query the existing table row
            var tableRow = $('#dynamicTableRow' + String(i));
            // Create a new table row to be inserted or replace the current one
            var newTableRow = $('<tr />', {'id': 'dynamicTableRow' + String(i)});
            var columnDataUrl = '/api/v1/admins/' + item.id;
            var username_td = $('<td />', {'data-title': 'Username: '}).append(
                $('<a />', {'href': '#', 'class': 'adminUsername', 'data-pk': item.id, 'data-url': columnDataUrl,
                            'title': 'Click to change the username'}).text(item.username)
            );
            var password_td = $('<td />', {'data-title': 'Password: '}).append(
                $('<a />', {'href': '#', 'class': 'adminPassword', 'data-pk': item.id, 'data-url': columnDataUrl,
                            'title': 'Click to change the password'}).text('●●●●●●●●')
            );
            var name_td = $('<td />', {'data-title': 'Name: '}).append(
                $('<a />', {'href': '#', 'class': 'adminName', 'data-pk': item.id, 'data-url': columnDataUrl,
                            'title': 'Click to change the name'}).text(item.name)
            );
            var locked_td = $('<td />', {'data-title': 'Locked: '});
            if (item.locked) {
                locked_td.append(
                    $('<a />', {'href': '#', 'class': 'adminLocked', 'data-pk': item.id,
                                'title': 'Click to unlock the administrator'}).text('Locked')
                );
            }
            else {
                locked_td.text('Unlocked');
            }
            var action_td = $('<td />', {'data-title': 'Action: '}).append(
                $('<a />', {'href': '#', 'class': 'deleteAnchor', 'data-pk': item.id, 'data-toggle': 'modal',
                            'data-target': '#deleteModal'}).text('Delete')
            );
            // Add the new columns to the new table row
            newTableRow.append(username_td).append(password_td).append(name_td).append(locked_td).append(action_td);
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
        setPagination(result['meta']['page'], pages, 'admins');
        //Activate x-editable on new elements and other events
        editableAdminEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        // Remove the loading spinner
        manageSpinner(false);
        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('admins');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Sets the default event listeners
    adminEventListeners();

    // Populate the table
    fillInTable();
});
