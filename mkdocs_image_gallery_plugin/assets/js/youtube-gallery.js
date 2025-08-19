(function() {
	function onClickPlay(event) {
		const card = event.currentTarget.closest('.yt-card');
		if (!card) return;
		const embedUrl = card.getAttribute('data-embed-url');
		if (!embedUrl) return;
		const container = card.querySelector('.yt-embed');
		if (!container) return;
		container.innerHTML = '<iframe width="560" height="315" src="' + embedUrl + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen loading="lazy"></iframe>';
		card.classList.add('is-playing');
	}

	function init() {
		document.querySelectorAll('.yt-card .yt-play').forEach(function(btn) {
			btn.addEventListener('click', onClickPlay, { passive: true });
		});
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
})();


