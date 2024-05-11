$(document).ready(function(){  
    $('.saved').hide();
    $('.waiting').hide();
    $('.expired').hide();
    $('.viewed').hide();
    $('#upload').click(function() {
        $('.upload').show();
        $('.saved').hide();
        $('.waiting').hide();
        $('.expired').hide();
        $('.viewed').hide();
        $('#upload').addClass("active");
        $('#saved').removeClass("active");
        $('#waiting').removeClass("active");
        $('#expired').removeClass("active");
        $('#viewed').removeClass("active");
    })
    $('#saved').click(function() {
        $('.saved').show();
        $('.upload').hide();
        $('.waiting').hide();
        $('.expired').hide();
        $('.viewed').hide();
        $('#saved').addClass("active");
        $('#upload').removeClass("active");
        $('#waiting').removeClass("active");
        $('#expired').removeClass("active");
        $('#viewed').removeClass("active");
    })
    $('#waiting').click(function() {
        $('.saved').hide();
        $('.upload').hide();
        $('.expired').hide();
        $('.waiting').show();
        $('.viewed').hide();
        $('#waiting').addClass("active");
        $('#upload').removeClass("active");
        $('#saved').removeClass("active");
        $('#expired').removeClass("active");
        $('#viewed').removeClass("active");
    })
    $('#expired').click(function() {
        $('.saved').hide();
        $('.upload').hide();
        $('.expired').show();
        $('.waiting').hide();
        $('.viewed').hide();
        $('#waiting').removeClass("active");
        $('#upload').removeClass("active");
        $('#saved').removeClass("active");
        $('#expired').addClass("active");
        $('#viewed').removeClass("active");
    })
    $('#viewed').click(function() {
        $('.saved').hide();
        $('.upload').hide();
        $('.expired').hide();
        $('.waiting').hide();
        $('.viewed').show();
        $('#waiting').removeClass("active");
        $('#upload').removeClass("active");
        $('#saved').removeClass("active");
        $('#expired').removeClass("active");
        $('#viewed').addClass("active");
    })
    setTimeout(function() {
        $('.alert-success').fadeOut('fast');
    }, 5000);
    const unit = ['VNĐ', 'nghìn đồng', 'triệu đồng', 'tỷ đồng']
    $('.display-price').html((idx, item) => {
        let i = 0;
        var price = parseFloat(item.split(" ").reverse()[1]);
        while(price >= 1000){
            if (i == 3){
                break;
            }
            i = i + 1;
            price = price/1000;
        }
        return ` Giá: ${price} ${unit[i]}`;
        
    });
    const queryString = window.location.search,
    urlParams = new URLSearchParams(queryString);
    if (urlParams.has("viewed")) {
        $('#viewed').click();
    }

})
