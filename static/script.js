

$('#navigation a').on('click', function (e) {
  e.preventDefault()
  $(this).animate().tab('show')
})

window.setTimeout(function () {
  $(".alert").animate({ 'top': '-70px' }, 500)
}, 4000);

// Add to favorites button function call
$(function () {
  $(".add").bind('click', function (e) {
    const left = e.pageX - 28;
    const top = e.pageY;
    $(".add-star").css({ top: top + "px", left: left + "px" });
    $(".add-star")
      .animate({ opacity: 1, top: "-=50px" }, 200, "linear")
      .animate({ top: "-=30px" }, 600, "linear")
      .animate({ opacity: 0, top: "-=150px" }, 200, "linear",
        function () {
          $(".add-star").css({ top: "50%" });
        }
      );
    $.ajax({
      url: '/add_to_favorites',
      data: { id: this.name, path: window.location.pathname },
      type: 'POST'
    });
  });
});

// Delete from favorites function call
$(function () {
  let recipe_id = 0;
  $(".my-buttons .delete").click(function () {
    recipe_id = this.name;
    $('body').css({ overflow: 'hidden' })
    $('.favoritesOverlay').show().animate({ opacity: 1 }, 300)
    $('.deleteFavDialog').css({ 'transform': 'scale(1)' })
  });
  $('.deleteFavDialog .close, .favoritesOverlay').click(function () {
    $('body').css({ overflow: 'initial' })
    $('.deleteFavDialog').css({ 'transform': 'scale(0)' })
    $('.favoritesOverlay').animate({ opacity: 0 }, 300).hide()
  });

  $('.recipeDeletion').on('click', function () {
    const select = $('.delete').filter(function (i, val) {
      if (val.name === recipe_id) {
        return val;
      }
    });
    $('.deleteFavDialog').css({ 'transform': 'scale(0)' })
    $('.favoritesOverlay').hide()
    $('body').css({ overflow: 'initial' })
    const card = select.parent().parent();
    setTimeout(function () {
      card.css({ 'transform': 'scale(0)' });
      setTimeout(function () {
        card.hide();
      }, 300);
    }, 300);
    $.ajax({
      url: '/delete_from_favorites',
      data: { id: recipe_id },
      type: 'POST'
    });
  });
});

// Share to feed function call
$(function () {
  $(".share").off().on('click', function () {
    let id = this.name;
    $('body').css({ overflow: 'hidden' })
    $('.shareOverlay').show().animate({ opacity: 1 }, 300)
    $(".postWindow").css({ 'transform': 'scale(1)' })
    $(".sharePost").off().on('click', function () {
      let postMsg = $("#postMsg").val();
      $.ajax({
        url: '/share_to_feed',
        data: { id: id, msg: postMsg },
        type: 'POST',
        success: setTimeout(function () {
          location.href = "/feed"
        }, 200)
      });
    });
    $(".postWindow .close, .shareOverlay").off().on('click', function () {
      $(".postWindow").css({ 'transform': 'scale(0)' })
      $('.shareOverlay').animate({ opacity: 0 }, 300).hide()
      $('body').css({ overflow: 'initial' })
      setTimeout(function () {
        $('#postMsg').val('')
      }, 200);
    });
  });
});

// Delete user
$(function () {
  $('.deleteAccount').click(function () {
    $('.overlay').show().animate({ opacity: 1 }, 300)
    $('.deleteDialog').css({ 'transform': 'scale(1)' })
  });
  $('.deleteDialog .close, .overlay').click(function () {
    $('.deleteDialog').css({ 'transform': 'scale(0)' })
    $('.overlay').animate({ opacity: 0 }, 300).hide()
  });
  $('.deletionConfirmed').on('click', function () {
    let checked = $('#deletionConfirm')[0].checked
    if (checked) {
      $.ajax({
        url: '/user_delete',
        type: 'POST',
        success: location.href = '/login'
      });
    }
  });
});

// Diet info window
$(function () {
  $('.diet-info-btn').click(function () {
    $('.overlay').show().animate({ opacity: 1 }, 300)
    $('.dietInfo').css({ 'transform': 'scale(1)' })
  });
  $('.dietInfo .close, .overlay').click(function () {
    $('.dietInfo').css({ 'transform': 'scale(0)' })
    $('.overlay').animate({ opacity: 0 }, 300).hide()
  });
});

// Advanced search form validation
$(function () {
  $('.advSearchWrap form').submit(function (e) {
    const advSearchVal = $('.advSearchWrap .input-group input').val();
    if (advSearchVal === '') {
      validate($('.advSearchWrap form .input-group'), "Search field cannot be empty");
      e.preventDefault();
    }
  });
});

// Index search validation
$(function () {
  $('.searchWrap form').submit(function (e) {
    const searchVal = $('.searchWrap input').val();
    if (searchVal === '') {
      $('.message').css({
        "background-color": "rgba(255,255,255,.7)",
        "padding": "5px 10px",
        "border-radius": "5px"
      });
      validate($('.searchWrap .input-group'), "Search field cannot be empty");
      e.preventDefault();
    }
  });
});

// Profile page validation
$(function () {
  const form = $('.profileContainer form');
  form.submit(function (e) {
    let good = true;
    let currPass = $('.profileContainer input[name="curr-pass"]').val().trim();
    let newPass = $('.profileContainer input[name="new-pass"]').val().trim();
    let confirmPass = $('.profileContainer input[name="confirm-pass"]').val().trim();

    if (currPass === '') {
      validate($('.profileContainer .pass-group'), "You must provide password");
    } else {
      removeError($('.profileContainer .pass-group'));
    }

    if (newPass === '') {
      validate($('.profileContainer .new-pass-group'), "You must provide new password");
      good = false;
    } else if (newPass.length < 6) {
      validate($('.profileContainer .new-pass-group'), "Password must be 6 letters or longer");
      good = false;
    }

    else {
      removeError($('.profileContainer .new-pass-group'));
    }

    if (confirmPass === '') {
      validate($('.profileContainer .confirm-group'), "You must confirm new password");
      good = false;
    } else if (newPass != confirmPass) {
      validate($('.profileContainer .confirm-group'), "Passwords must match");
      good = false;
    } else {
      removeError($('.profileContainer .confirm-group'));
    }


    if (good) {
      form.submit();
    } else {
      e.preventDefault();
    }
  });
});

// Login page validation
$(function () {
  const form = $('.loginForm form');

  form.submit(function (e) {
    let good = true;
    const username = $('.loginForm .username input').val().trim();
    const password = $('.loginForm .password input').val().trim();

    if (username === '') {
      validate($('.loginForm .username'), 'You must provide username');
      good = false;
    } else {
      removeError($('.loginForm .username'));
    }

    if (password === '') {
      validate($('.loginForm .password'), 'You must provide password');
      good = false;
    } else {
      removeError($('.loginForm .password'));
    }

    if (good) {
      form.submit();
    } else {
      e.preventDefault();
    }
  });
});

// Register page validation
// Login page validation
$(function () {
  const form = $('.registerForm form');

  form.submit(function (e) {
    let good = true;
    const username = $('.registerForm .username input').val().trim();
    const password = $('.registerForm .password input').val().trim();
    const confirm = $('.registerForm .confirm input').val().trim();

    if (username === '') {
      validate($('.registerForm .username'), 'You must provide username');
      good = false;
    } else {
      removeError($('.registerForm .username'));
    }

    if (password === '') {
      validate($('.registerForm .password'), 'You must provide password');
      good = false;
    } else if (password.length < 6) {
      validate($('.registerForm .password'), "Password must be 6 letters or longer");
      good = false;
    } else {
      removeError($('.registerForm .password'));
    }

    if (confirm === '') {
      validate($('.registerForm .confirm'), 'You must confirm password');
      good = false;
    } else if (password != confirm) {
      validate($('.registerForm .confirm'), "Passwords must match");
      good = false;
    } else {
      removeError($('.registerForm .confirm'));
    }



    if (!$('.my-checkbox input').is(":checked")) {
      validate($('.my-checkbox'), "You must agree with terms and conditions");
      good = false;
    } else {
      removeError($('.my-checkbox'));
    }

    if (good) {
      form.submit();
    } else {
      e.preventDefault();
    }
  });
});

// Client side form validation function
function validate(groupSelector, message) {
  groupSelector.children('input').addClass('error');
  groupSelector.children('.message').text(message);
};

// Remove 'error' class
function removeError(groupSelector) {
  groupSelector.children('input').removeClass('error');
  groupSelector.children('.message').text('');
}