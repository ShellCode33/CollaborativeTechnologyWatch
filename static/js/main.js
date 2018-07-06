let topics = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
        url: '/suggest/topic/%QUERY',
        wildcard: '%QUERY'
    }
});

let tags = new Bloodhound({
    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    prefetch: '/suggest/tag/*',
    remote: {
        url: '/suggest/tag/%QUERY',
        wildcard: '%QUERY'
    }
});

function scrollTo(id) {
    console.log("Scroll to #" + id);
    $("html, body").animate({ scrollTop: $('#' + id).offset().top }, 1000);
}

$(function() {

    let search_input_width = $("#search-input").outerWidth() - 3;

    $(window).scroll(function() {
        let current;

        $( "section" ).each(function( index ) {
            if($(this).offset().top - $(document).scrollTop() < $(window).height() / 2) {// si la div occupe plus de la moitier de l'écran, on active le nav-item
                current = $(this).attr('id');
            }
        });

        $(".nav-item").removeClass("active");
        $("#nav-item-" + current).addClass("active");
    });

    $(window).trigger('scroll');

    $('#search-form .typeahead').typeahead({
        highlight: true,
        minLength: 3
    }, {
        name: 'searchTopics',
        display: function (item) {
            return "topic:" + item.name;
        },
        source: topics,
        templates: {
            header: '<h3 class="suggestions-header">Sujets</h3>',
            suggestion: function (response) {
                return $("<div>").text(response.name);
            }
        }
    }, {
        name: 'searchTags',
        display: function (item) {
            return "tag:" + item.name;
        },
        source: tags,
        templates: {
            header: '<h3 class="suggestions-header">Tags</h3>',
            suggestion: function (response) {
                return $("<div>").text(response.name);
            }
        }
    });

    //Restore input width altered by Bloodhound
    $("#search-input").css("width", search_input_width + "px");

    $("#create-new-topic-button").click(function () {
        let post_parameters = $('#new-topic-form').serialize();

        $(".tag-input").each(function (i, tag) {
            post_parameters += "&tag=" + encodeURIComponent(tag.innerText);
        });

        $.ajax({
            url: '/topic/new/',
            type: 'post',
            data: post_parameters
        }).done(function (new_tags) {
            $("#create-topic-modal").modal('toggle');
            $("#topic-created-modal").find(".modal-body").remove();
            $("#topic-created-modal").find(".modal-header").after($(new_tags));
            $("#topic-created-modal").modal('toggle');
        }).fail(function (data) {
            $("#error-new-topic .error-message").text(data["responseJSON"].error);
            $("#error-new-topic").removeAttr('hidden');
        });
    });

    $("#search-form").submit(function (e) {
        if($("#search-input").val().length < 3) {
            $("#message-modal .modal-title").text("Erreur");
            $("#message-modal .modal-body").html("Merci de faire une recherche d'au minimum 3 caractères.");
            $("#message-modal").modal('toggle');
            e.preventDefault();
        }
    });

    $("#search-input").keypress(function (e) {
        if(e.which === 13)
            $("#search-form").submit();
    });

    //Keep only one item opened in the news
    $(".latest-group-item").focusout(function () {
        $("[id^=latest-topic-description-]").collapse("hide");
    });

    $(".hottest-group-item").focusout(function () {
        $("[id^=hottest-topic-description-]").collapse("hide");
    });

    $("#add-resource-form button").click(function () {
        $.ajax({
            url: '/topic/' + $("#topic_id").text() + '/addresource/',
            type: 'post',
            dataType: 'json',
            data: $('#add-resource-form').serialize()
        }).done(function (data) {
            $("#message-modal .modal-title").text("Information");
            $("#message-modal .modal-body").html(data.message);
            $("#message-modal").modal('toggle');
            let linkname = $("#add-resource-form input[name='link-name']").val();
            let link = $("#add-resource-form input[name='link']").val();
            let new_res = $('<a class="btn btn-success resource-button" href="' + link + '" target="_blank">' + linkname + '</a>');
            $("#resources").append(new_res);

        }).fail(function (error) {
            $("#message-modal .modal-title").text("Erreur");
            $("#message-modal .modal-body").html(error["responseJSON"].message);
            $("#message-modal").modal('toggle');
        });
    });

    $("#like-button").click(function () {
        let like_button = $("#like-button");
        let not_liked_yet = like_button.hasClass("btn-success");

        $.ajax({
            url: '/topic/' + $("#topic_id").text() + (not_liked_yet ? '/like/' : '/removelike/'),
            type: 'post',
            data: $('input[name="csrfmiddlewaretoken"]').serialize()
        }).done(function (data) {
            let likes_count = $("#likes-count");

            if(not_liked_yet) {
                likes_count.text(parseInt(likes_count.text()) + 1);
                like_button.text("Je n'aime plus");
                like_button.removeClass("btn-success");
                like_button.addClass("btn-danger");
            }

            else {
                likes_count.text(parseInt(likes_count.text()) - 1);
                like_button.text("J'aime");
                like_button.removeClass("btn-danger");
                like_button.addClass("btn-success");
            }
        }).fail(function (data) {
            $("#message-modal .modal-title").text("Erreur");
            $("#message-modal .modal-body").html(data["responseJSON"].error);
            $("#message-modal").modal('toggle');
        });
    });

    let tags_input = $("#tags-input");
    let tag_input = tags_input.find("input");

    tag_input.keypress(function (e) {
        if(e.which === 13 || e.which === 32) {
            let new_tag = $("<span class=\"tag-input badge badge-success mr-2\">" + $(this).val() + "<i class=\"remove-tag fa fa-times fa-white\"></i></span>");

            new_tag.children(".remove-tag").click(function () {
                new_tag.remove();
            });

            tags_input.find(".twitter-typeahead").before(new_tag);
            tag_input.val("");
            e.preventDefault();
        }
    });

    tag_input.typeahead({
        highlight: true,
        minLength: 2
    }, {
        name: 'searchTags',
        display: function (item) {
            return item.name;
        },
        source: tags,
        templates: {
            suggestion: function (response) {
                return $("<div>").text(response.name);
            }
        }
    });

    $("#ressource-input button").click(function () {
        add_ressource();
    });

    $("#tags-input").click(function () {
        $(this).find("input").focus();
    });

    $("#connect-button").click(function () {
        $.ajax({
            url: '/connect/',
            type: 'post',
            data: $('#login-modal input').serialize()
        }).done(function (data) {
            location.reload();
        }).fail(function (data) {
            $("#error-login .error-message").text(data["responseJSON"].error);
            $("#error-login").removeAttr('hidden');
        });
    });
});

function add_ressource() {
    let current_input = $("#ressource-input");
    let link_name_value = current_input.find("input[name='link-name']").val();
    let link = current_input.find("input[name='link']");

    if(!link.val().startsWith("http://") && !link.val().startsWith("https://")) {
        link.val("https://");
        link.focus();
        $("#error-new-topic .error-message").html("Le lien doit commencer par <b>http(s)://</b>");
        $("#error-new-topic").removeAttr('hidden');
        return;
    }

    let current_button = current_input.find("button");
    let new_ressource = current_input.clone();
    new_ressource.children("input").val("");
    new_ressource.find("button").click(add_ressource);
    current_input.attr("id", ""); //Prevent duplicate id
    current_button.off("click");

    current_button.removeClass("btn-success").addClass("btn-danger");
    current_button.find("i").removeClass("fa-plus").addClass("fa-times");

    current_button.click(function () {
        current_input.remove();
    });

    $("#ressources").append(new_ressource);
    new_ressource.children("input[name='link-name']").focus();
}