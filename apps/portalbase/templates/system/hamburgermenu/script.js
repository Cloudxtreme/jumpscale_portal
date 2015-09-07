var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = decodeURIComponent(window.location.search.substring(1)),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : sParameterName[1];
        }
    }
};

function injectIframe() {
    $('.flatTheme > .container').html('');
    $('.flatTheme > .container').addClass('height-full');
    $('.flatTheme > .container').html("<iframe id='external-iframe' class='border-none' src='" + getUrlParameter('url') + "'></iframe>");
    $('.flatTheme > .container').removeClass('container');
    $('.navbar-inverse').remove();
    $('.flatTheme').addClass('padding-top-none');
    $('.navmenu-fixed-left.offcanvas').remove();
    $('.height-full').prepend("<div class='navmenu navmenu-default navmenu-fixed-left offcanvas'><a class=''>{{hrdListHTML}}</a></div>");
}

function injectHamburgerButton(portalType) {
    if(portalType == "wiki_gcb" || portalType == "dcpm"){
        $('.height-full').prepend("<button id='PortalsHamburgerMenu' class='c-hamburger c-hamburger--htla dark left position-fixed position-top-medium position-left-medium' title='Portals' data-toggle='offcanvas' data-target='.navmenu' data-canvas='body'><span>toggle hamburger</span></button>");
    }else{
        $('.height-full').prepend("<button id='PortalsHamburgerMenu' class='c-hamburger c-hamburger--htla white left position-fixed position-top-medium position-left-medium' title='Portals' data-toggle='offcanvas' data-target='.navmenu' data-canvas='body'><span>toggle hamburger</span></button>");
    }
    $('body').click();
}


$( function () {
    $('.navbar-inner.navbar-form').prepend("<div class='navmenu navmenu-default navmenu-fixed-left offcanvas'>{{hrdListHTML}}</div>");
    $('.navbar-inner.navbar-form').prepend("<button id='PortalsHamburgerMenu' class='c-hamburger c-hamburger--htla white left' title='Portals' data-toggle='offcanvas' data-target='.navmenu' data-canvas='body'><span>toggle hamburger</span></button>");


    var currentPage = '';
    if(window.location.pathname.indexOf('external') > -1){
        currentPage = 'external';
    }

    if(currentPage == 'external'){


        var portalType = '';
        if(getUrlParameter('url').indexOf("wiki_gcb") > -1){
            portalType = "wiki_gcb";
        }
        if(getUrlParameter('url').indexOf("dcpm") > -1){
            portalType = "dcpm";
        }
        injectIframe();
        injectHamburgerButton(portalType);
    }

    $( ".openIframe" ).click(function(event) {
        var portalType = '';
        if(this["href"].indexOf("wiki_gcb") > -1){
            portalType = "wiki_gcb";
        }
        if(this["href"].indexOf("dcpm") > -1){
            portalType = "dcpm";
        }
        if(this["href"].indexOf(document.location.hostname) == -1 || portalType == "wiki_gcb"){
            event.preventDefault();
            window.location.replace("/home/external?url=" + this["href"]);
            injectIframe();
            injectHamburgerButton(portalType);
        }

    });
});
