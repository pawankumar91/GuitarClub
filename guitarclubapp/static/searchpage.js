var main = function() {
  $('.search_bar > li').bind('mouseenter', openSubMenu);
  $(document).bind('click', closeSubMenu1);
  $('.profile-menu > li').bind('mouseover', openSubMenu);
  $(document).bind('click',closeSubMenu);

  function openSubMenu() {
  $(this).find('ul').css('visibility', 'visible');
  };

  function closeSubMenu() {
  $('.profile-menu > li').find('ul').css('visibility', 'hidden');
  };

  function closeSubMenu1() {
  $('.search_bar > li').find('ul').css('visibility', 'hidden');
  };
}

$(document).ready(main);