<?php
/**
 * Title: Pied de page et barre mobile
 * Slug: valoris/pied-de-page
 * Categories: valoris
 * Inserter: no
 */
?>
<!-- wp:group {"tagName":"footer","className":"vp-footer","layout":{"type":"default"}} -->
<footer class="wp-block-group vp-footer"><!-- wp:group {"className":"vp-inner","layout":{"type":"default"}} -->
<div class="wp-block-group vp-inner"><!-- wp:group {"className":"vp-footer__haut","layout":{"type":"default"}} -->
<div class="wp-block-group vp-footer__haut"><!-- wp:group {"layout":{"type":"default"}} -->
<div class="wp-block-group"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"vp-logo"} -->
<figure class="wp-block-image size-full vp-logo"><a href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/logo-valoris-clair.svg' ) ); ?>" alt="VALORIS PATRIMOINE, accueil"/></a></figure>
<!-- /wp:image -->

<!-- wp:paragraph -->
<p>Location directe d'appartements meublés auprès de propriétaires, mis à disposition de professionnels en déplacement. Priorité Île-de-France.</p>
<!-- /wp:paragraph --></div>
<!-- /wp:group -->

<!-- wp:group {"layout":{"type":"default"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Le site</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/proprietaires/' ) ); ?>">Propriétaires</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/entreprises/' ) ); ?>">Entreprises</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/notre-societe/' ) ); ?>">Notre société</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">Contact</a></li>
<!-- /wp:list-item --></ul>
<!-- /wp:list --></div>
<!-- /wp:group -->

<!-- wp:group {"layout":{"type":"default"}} -->
<div class="wp-block-group"><!-- wp:heading -->
<h2 class="wp-block-heading">Contact</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li>[Téléphone]</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>[WhatsApp]</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>[Email]</li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li>[Adresse du siège]</li>
<!-- /wp:list-item --></ul>
<!-- /wp:list --></div>
<!-- /wp:group --></div>
<!-- /wp:group -->

<!-- wp:group {"className":"vp-footer__bas","layout":{"type":"default"}} -->
<div class="wp-block-group vp-footer__bas"><!-- wp:paragraph -->
<p>© 2026 [Dénomination juridique]</p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/mentions-legales/' ) ); ?>">Mentions légales</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/politique-de-confidentialite/' ) ); ?>">Politique de confidentialité</a></li>
<!-- /wp:list-item -->

<!-- wp:list-item -->
<li><a href="<?php echo esc_url( home_url( '/cookies/' ) ); ?>">Cookies</a></li>
<!-- /wp:list-item --></ul>
<!-- /wp:list --></div>
<!-- /wp:group --></div>
<!-- /wp:group --></footer>
<!-- /wp:group -->

<!-- wp:group {"className":"vp-barre-mobile","layout":{"type":"default"}} -->
<div class="wp-block-group vp-barre-mobile"><!-- wp:buttons -->
<div class="wp-block-buttons"><!-- wp:button {"className":"is-style-secondaire vp-ico-tel"} -->
<div class="wp-block-button is-style-secondaire vp-ico-tel"><a class="wp-block-button__link wp-element-button" href="tel:+33000000000">Appeler</a></div>
<!-- /wp:button -->

<!-- wp:button {"className":"is-style-secondaire vp-ico-whatsapp"} -->
<div class="wp-block-button is-style-secondaire vp-ico-whatsapp"><a class="wp-block-button__link wp-element-button" href="https://wa.me/33000000000">WhatsApp</a></div>
<!-- /wp:button -->

<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="<?php echo esc_url( home_url( '/proprietaires/#etude-logement' ) ); ?>">Étudier mon logement</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group -->
