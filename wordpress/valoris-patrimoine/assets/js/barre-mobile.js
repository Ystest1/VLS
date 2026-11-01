/* Barre d'action mobile : repliée tant que les boutons du premier écran (bloc Boutons portant
   la classe « vp-actions » dans la section « vp-hero ») sont visibles, affichée dès qu'ils sortent
   de l'écran. Sans JavaScript, ou sur une page sans premier écran, la barre reste affichée. */
(function () {
	var barre = document.querySelector('.vp-barre-mobile');
	var boutons = document.querySelector('.vp-hero .vp-actions');
	if (!barre || !boutons || !('IntersectionObserver' in window)) return;
	var r = boutons.getBoundingClientRect();
	barre.classList.toggle('vp-barre-mobile--repliee', r.bottom > 0 && r.top < window.innerHeight);
	new IntersectionObserver(function (entrees) {
		barre.classList.toggle('vp-barre-mobile--repliee', entrees[0].isIntersecting);
	}).observe(boutons);
})();
