(function() {

	// var canCss3 = "localstorage" in window;
	// var shiftProperty = function(value) {
	// 	return canCss3 ? 
	// 		{transform: translateX(value+"px")}
	// 		: {left: translateX(value+"px")};
	// }

	// function slide() {}
	// slide.prototype.toleft = function() {
	// 	var items = $(this.el).children('.item');
	// 	items.each(function(index, el) {
	// 		$(el).animate(shiftProperty(80),
	// 		{
	// 			easing: "ease",
	// 			duration: 500
	// 		});
	// 	});
	// }

	// slide.prototype.toright = function() {
	// 	var items = $(this.el).children('.item');
	// 	items.each(function(index, el) {
	// 		$(el).animate(shiftProperty(-80),
	// 		{
	// 			easing: "ease",
	// 			duration: 500
	// 		});
	// 	});
	// }

	// function sliderEvent(fn, id) {
	// 	var type = this.types[id];
	// 	type[type.length] = fn;
	// }
	// sliderEvent.prototype.father = $(".user-select");
	// sliderEvent.prototype.types = [];
	// sliderEvent.prototype.fire = function() {
	// 	var i;
	// 	var types = this.types;
	// 	var fa = this.father;
	// 	var curly = function() {
	// 		var fns = $.isArray(arguments[0]) ?
	// 					arguments[0] 
	// 					: arguments;
	// 		return function() {
	// 			for(var i = 0, len = fns.length; i < len; i++) {
	// 				typeof fns[i] === "function" && fns[i]();
	// 			}
	// 		};
	// 	}
	// 	for(i in types) {
	// 		$(this.father).on("click", "."+i, curly(types));
	// 	}
	// }

	// var Slider = function() {

	// };

	var appear = {
		face: {
			el: $(".face"),
			nowSrc: "-"
		},
		hair: {
			el: $(".hair"),
			nowSrc: "-"
		},
		glass: {
			el: $(".glass"),
			nowSrc: "-"
		},
		suit: {
			el: $(".suit"),
			nowSrc: "-"
		},
		shoes: {
			el: $(".shoes"),
			nowSrc: "-"
		},
		prop: {
			el: $(".prop"),
			nowSrc: "-"
		},
		bg: {
			el: $(".body-wr"),
			nowSrc: "-"
		}
	};

	$(".styles").on("click", ".item img", function(e) {
		e.preventDefault();
		var tar = e.target;
		var ty = $(tar).attr("alt");
		var src;
		var lastSelect;
		if(ty != "bg") {
			src = $(tar).attr("src");
			lastSelect = $("img[src='" + appear[ty].nowSrc +"']");
		} else {
			src = $(tar).data("color");
			lastSelect = $("img[data-color='" + appear[ty].nowSrc +"']");
		}
		if(src != appear[ty].nowSrc) {
			if(appear[ty].nowSrc.indexOf("prop-5") > -1) {
				$(".bag").attr("src", "");
				$(".bag-belt").attr("src", "");
			} else if(appear[ty].nowSrc.indexOf("prop-4") > -1) {
				appear[ty].el.removeClass("panel");
				appear[ty].el.attr("src", "");
			} else if(appear[ty].nowSrc.indexOf("prop-2") > -1) {
				appear[ty].el.removeClass("basketball");
				appear[ty].el.attr("src", "");
			} else {
				appear[ty].el.attr("src", "");
			}
			if(ty == "prop" && src.indexOf("prop-5") > -1) {
				$(".bag").attr("src", "static/image/bag.png");
				$(".bag-belt").attr("src", "static/image/bag-belt.png");
			} else if(ty == "prop" && src.indexOf("prop-4") > -1) {
				appear[ty].el.addClass("panel");
				appear[ty].el.attr("src", src.replace("/block-icons", ""));
			} else if(ty == "prop" && src.indexOf("prop-2") > -1) {
				appear[ty].el.addClass("basketball");
				appear[ty].el.attr("src", src.replace("/block-icons", ""));
			} else if(ty != "bg") {
				appear[ty].el.attr("src", src.replace("/block-icons", ""));
			} else {
				appear[ty].el.css("background-color", src);
			}
			lastSelect && lastSelect.parent().removeClass("selected");
			appear[ty].nowSrc = src;
			$(tar).parent().addClass('selected');
		} else {
			if(ty != "bg") {
				lastSelect && lastSelect.parent().removeClass("selected");
				if(ty == "prop" && src.indexOf("prop-5") > -1) {
					$(".bag").attr("src", "");
					$(".bag-belt").attr("src", "");
				} else if(ty == "prop" && src.indexOf("prop-4") > -1) {
					appear[ty].el.removeClass("panel");
				} else if(ty == "prop" && src.indexOf("prop-2") > -1) {
					appear[ty].el.removeClass("basketball");
				}
				appear[ty].el.attr("src" , "");
				appear[ty].nowSrc = "-";
			}
		}
	});

	function slideToLeft(el) {
		var dom = el.find(".items");
		if(parseInt(dom.css("margin-left")) >= 0 || $(":animated").length > 0) return ;
		dom.animate({
			marginLeft: "+=80px"
		}, {
			duration: 500
		});
	}

	function slideToRight(el) {
		var dom = el.find(".items");
		if(parseInt(dom.css("margin-left")) < -(dom.find(".item").length*80 - 400) || $(":animated").length > 0) return;
		dom.animate({
			marginLeft: "-=80px"
		}, {
			duration: 500
		});
	}

	$(".items").each(function(index, el) {
		$(el).css("margin-left", 0);
	})

	$(".styles").on('click', '.arrow', function(e) {
		e.preventDefault();
		var tar = e.target;
		if($(tar).hasClass("arrow-left")) {
			slideToLeft($(tar).parent());
		} else {
			slideToRight($(tar).parent());
		}
	});

	$(".ok-button").click(function(e) {
		e.preventDefault();
		var names = ["bag", "hair", "face", "glass", "suit", "shoes", "prop", "bg", "bag-belt"];
		$(names).each(function(index, name) {
			if(name == "bag" || name == "bag-belt") {
				$("#_" + name).val($("#" + name).attr("src"));
			} else {
				$("#_" + name).val(appear[name].nowSrc);
			}
		});
		$("#ok-form").submit();
	});

})();









