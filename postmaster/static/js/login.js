function pullDownLoginPanel() {
    var loginRow = $('#loginRow');
    var bodyHeight = $('#body').height();
    var navHeight = $('#navigation-bar').height();
    var loginRowHeight = loginRow.height();
    var marginTop = (bodyHeight - navHeight - loginRowHeight) / 3;
    if (marginTop > 10) {
        loginRow.css('margin-top', marginTop);
    }
    else {
        loginRow.css('margin-top', 10);
    }
}

$(document).ready(function () {
    pullDownLoginPanel();
});

$(window).resize(function () {
    pullDownLoginPanel();
});
