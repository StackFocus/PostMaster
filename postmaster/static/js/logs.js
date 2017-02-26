function formatDateNumber(num) {
    return String(num < 9 ? '0' + (num + 1) : num + 1);
}


function dateFormatFromISO(timestamp) {
    var date = new Date(timestamp);
    var suffix = (date.getHours() >= 12 ? 'PM' : 'AM');
    var minutes = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes());
    var hourInUsFormat = (date.getHours() + 11) % 12 + 1;
    var time = hourInUsFormat + ':' + minutes + ' ' + suffix;
    return dateString = formatDateNumber(date.getMonth()) + '/' + formatDateNumber(date.getDate()) + '/' + date.getFullYear() + ' ' + time;
}


// Loads the dynamic table and pagination
function fillInTable() {
    // Set the loading spinner
    manageSpinner(true);

    apiURL = '/api/v1/logs?reverse=1&lines=75';

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            // Query the existing table row
            var tableRow = $('#dynamicTableRow' + String(i));
            // Create a new table row to be inserted or replace the current one
            var newTableRow = $('<tr />', {'id': 'dynamicTableRow' + String(i)});
            var time_td = $('<td />', {'data-title': 'Time: '}).text(dateFormatFromISO(item.timestamp));
            var admin_td = $('<td />', {'data-title': 'Admin: '}).text(item.admin);
            var message_td = $('<td />', {'data-title': 'Message: '}).text(item.message);
            // Add the new columns to the new table row
            newTableRow.append(time_td).append(admin_td).append(message_td);

            // If the table row exists, then replace it, otherwise insert it
            if (tableRow.length > 0) {
                tableRow.replaceWith(newTableRow);
            }
            else {
                appendTableRow(newTableRow);
            }

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        // Remove the loading spinner
        manageSpinner(false);
        addStatusMessage('error', filterText(JSON.parse(jqxhr.responseText)['message']));
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Populate the table
    fillInTable();
});
