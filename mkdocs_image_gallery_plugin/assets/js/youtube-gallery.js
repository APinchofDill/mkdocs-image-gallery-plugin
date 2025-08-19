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
		holder.innerHTML = '<iframe src="' + urlWithAutoplay + '" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>';
		lb.classList.add('is-open');
		document.body.style.overflow = 'hidden';
	}

	function init() {
		document.querySelectorAll('.yt-card .yt-play').forEach(function(btn) {
			if (btn.dataset.ytBound === '1') return;
			btn.addEventListener('click', onClickPlay, { passive: true });
			btn.dataset.ytBound = '1';
		});

		document.querySelectorAll('.yt-card .yt-thumb').forEach(function(img) {
			// If the image is already cached/loaded
			if (img.complete && img.naturalWidth > 0) {
				markThumbLoaded(img);
			} else {
				if (img.dataset.ytBound !== '1') {
					img.addEventListener('load', function() { markThumbLoaded(img); }, { once: true });
					img.addEventListener('error', function() {
						// Avoid infinite skeleton if image fails to load
						markThumbLoaded(img);
					}, { once: true });
					img.dataset.ytBound = '1';
				}
			}
		});

		// Lightbox interactions
		const lb = document.querySelector('.yt-lightbox');
		if (lb) {
			if (!lb.dataset.ytBound) {
				lb.addEventListener('click', function(e) {
					if (e.target === lb) closeLightbox();
				});
				const closeBtn = lb.querySelector('.yt-lightbox-close');
				if (closeBtn) {
					closeBtn.addEventListener('click', function() { closeLightbox(); });
				}
				lb.dataset.ytBound = '1';
			}
			// Bind a single global keydown handler once
			if (!document._ytLightboxKeydownBound) {
				document.addEventListener('keydown', function(e) {
					const activeLb = document.querySelector('.yt-lightbox');
					if (e.key === 'Escape' && activeLb && activeLb.classList.contains('is-open')) closeLightbox();
				});
				document._ytLightboxKeydownBound = true;
			}
		}
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}

	// Support Material for MkDocs instant navigation: re-run on page swaps
	if (window.document$ && typeof window.document$.subscribe === 'function') {
		window.document$.subscribe(function() {
			init();
		});
	}
})();


