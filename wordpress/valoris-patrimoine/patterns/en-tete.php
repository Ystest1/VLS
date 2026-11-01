<?php
/**
 * Title: En-tête
 * Slug: valoris/en-tete
 * Categories: valoris
 * Inserter: no
 */
?>
<!-- wp:group {"className":"vp-inner","layout":{"type":"default"}} -->
<div class="wp-block-group vp-inner"><!-- wp:image {"sizeSlug":"full","linkDestination":"custom","className":"vp-logo"} -->
<figure class="wp-block-image size-full vp-logo"><a href="<?php echo esc_url( home_url( '/' ) ); ?>"><img src="<?php echo esc_url( get_theme_file_uri( 'assets/images/logo-valoris.svg' ) ); ?>" alt="VALORIS PATRIMOINE, accueil"/></a></figure>
<!-- /wp:image -->

<!-- wp:navigation {"overlayMenu":"mobile","ariaLabel":"Navigation principale","className":"vp-nav","layout":{"type":"flex","justifyContent":"center"}} -->
<!-- wp:navigation-link {"label":"Propriétaires","url":"<?php echo esc_url( home_url( '/proprietaires/' ) ); ?>","kind":"custom"} /-->

<!-- wp:navigation-link {"label":"Entreprises","url":"<?php echo esc_url( home_url( '/entreprises/' ) ); ?>","kind":"custom"} /-->

<!-- wp:navigation-link {"label":"Notre société","url":"<?php echo esc_url( home_url( '/notre-societe/' ) ); ?>","kind":"custom"} /-->

<!-- wp:navigation-link {"label":"Contact","url":"<?php echo esc_url( home_url( '/contact/' ) ); ?>","kind":"custom"} /-->
<!-- /wp:navigation -->

<!-- wp:buttons {"className":"vp-header__cta"} -->
<div class="wp-block-buttons vp-header__cta"><!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="<?php echo esc_url( home_url( '/proprietaires/#etude-logement' ) ); ?>">Étudier mon logement</a></div>
<!-- /wp:button --></div>
<!-- /wp:buttons --></div>
<!-- /wp:group -->
