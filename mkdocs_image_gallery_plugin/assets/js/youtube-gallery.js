(function() {
	function onClickPlay(event) {
		const card = event.currentTarget.closest('.yt-card');
		if (!card) return;
		const embedUrl = card.getAttribute('data-embed-url');
		if (!embedUrl) return;
		openLightbox(embedUrl);
	}

	function markThumbLoaded(imgEl) {
		if (!imgEl) return;
		imgEl.classList.add('loaded');
		const card = imgEl.closest('.yt-card');
		if (card) {
			card.classList.add('has-thumb-loaded');
		}
	}

	function closeLightbox() {
		const lb = document.querySelector('.yt-lightbox');
		if (!lb) return;
		lb.classList.remove('is-open');
		const holder = lb.querySelector('.yt-lightbox-embed');
		if (holder) holder.innerHTML = '';
		document.body.style.overflow = '';
	}

	function openLightbox(embedUrl) {
		const lb = document.querySelector('.yt-lightbox');
		if (!lb) return;
		const holder = lb.querySelector('.yt-lightbox-embed');
		if (!holder) return;
		const urlWithAutoplay = embedUrl.includes('?') ? (embedUrl + '&autoplay=1') : (embedUrl + '?autoplay=1');
		holder.innerHTML = '<iframe width="560" height="315" src="' + urlWithAutoplay + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
		lb.classList.add('is-open');
		document.body.style.overflow = 'hidden';
	}

	function init() {
		document.querySelectorAll('.yt-card .yt-play').forEach(function(btn) {
			btn.addEventListener('click', onClickPlay, { passive: true });
		});

		document.querySelectorAll('.yt-card .yt-thumb').forEach(function(img) {
			// If the image is already cached/loaded
			if (img.complete && img.naturalWidth > 0) {
				markThumbLoaded(img);
			} else {
				img.addEventListener('load', function() { markThumbLoaded(img); }, { once: true });
				img.addEventListener('error', function() {
					// Avoid infinite skeleton if image fails to load
					markThumbLoaded(img);
				}, { once: true });
			}
		});

		// Lightbox interactions
		const lb = document.querySelector('.yt-lightbox');
		if (lb) {
			lb.addEventListener('click', function(e) {
				if (e.target === lb) closeLightbox();
			});
			const closeBtn = lb.querySelector('.yt-lightbox-close');
			if (closeBtn) {
				closeBtn.addEventListener('click', function() { closeLightbox(); });
			}
			document.addEventListener('keydown', function(e) {
				if (e.key === 'Escape' && lb.classList.contains('is-open')) closeLightbox();
			});
		}
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}
})();


