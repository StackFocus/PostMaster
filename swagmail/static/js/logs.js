function formatDateNumber(num) {
    return String(num < 9 ? '0' + (num + 1) : num + 1);
}


function dateFormatFromISO(timestamp) {
    var date = new Date(timestamp);
    var suffix = (date.getHours() >= 12 ? 'PM' : 'AM')
    var minutes = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes())
    var hourInUsFormat = (date.getHours() + 11) % 12 + 1
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

        var i = 1
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-title="Time: ">' + dateFormatFromISO(item.timestamp) + '</td>\
                    <td data-title="Admin: ">' + item.admin + '</td>\
                    <td data-title="Message: ">' + item.message + '</td>'
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? appendTableRow(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {

        addStatusMessage('error', JSON.parse(jqxhr.responseText)['message']);
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Populate the table
    fillInTable();
});
