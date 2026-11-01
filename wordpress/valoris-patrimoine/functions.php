<?php
/**
 * Thème VALORIS PATRIMOINE — fonctions.
 *
 * Volontairement court : chargement des styles et du script de la barre mobile,
 * styles de boutons, catégorie de compositions, création de la page d'accueil
 * à l'activation (uniquement sur un site neuf).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Réglages du thème. */
add_action( 'after_setup_theme', function () {
	remove_theme_support( 'core-block-patterns' ); // Seules les compositions VALORIS sont proposées.
} );

/** Pas de script d'émojis de WordPress (il peut charger des images depuis s.w.org) : aucun appel externe. */
remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
remove_action( 'wp_print_styles', 'print_emoji_styles' );

/** Classe « vp-site » sur <body> : tous les styles du thème en dépendent. */
add_filter( 'body_class', function ( $classes ) {
	$classes[] = 'vp-site';
	return $classes;
} );

/** Styles du thème : sur le site et dans l'éditeur (même rendu). */
add_action( 'enqueue_block_assets', function () {
	$fichier = get_theme_file_path( 'assets/css/valoris.css' );
	wp_enqueue_style( 'valoris', get_theme_file_uri( 'assets/css/valoris.css' ), array(), filemtime( $fichier ) );
} );

/** Barre d'action mobile : repliée tant que les boutons du premier écran sont visibles. */
add_action( 'wp_enqueue_scripts', function () {
	$fichier = get_theme_file_path( 'assets/js/barre-mobile.js' );
	wp_enqueue_script( 'valoris-barre-mobile', get_theme_file_uri( 'assets/js/barre-mobile.js' ), array(), filemtime( $fichier ), array( 'in_footer' => true, 'strategy' => 'defer' ) );
} );

/** Préchargement de la police des titres. */
add_action( 'wp_head', function () {
	printf(
		'<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n",
		esc_url( get_theme_file_uri( 'assets/fonts/playfair-display-var.woff2' ) )
	);
}, 1 );

/** Styles de boutons (choix dans le panneau « Styles » du bloc Bouton). */
add_action( 'init', function () {
	register_block_style( 'core/button', array( 'name' => 'secondaire', 'label' => 'Secondaire (contour)' ) );
	register_block_style( 'core/button', array( 'name' => 'clair', 'label' => 'Champagne (fond foncé)' ) );
	register_block_style( 'core/button', array( 'name' => 'contour-clair', 'label' => 'Contour clair (fond foncé)' ) );

	register_block_pattern_category( 'valoris', array( 'label' => 'VALORIS PATRIMOINE' ) );
} );

/**
 * À l'activation du thème, sur un site neuf uniquement (aucune page d'accueil statique
 * définie et aucune page « accueil ») : crée la page « Accueil » avec toutes les sections
 * et la définit comme page d'accueil. Sur un site existant, rien n'est modifié.
 */
add_action( 'after_switch_theme', function () {
	if ( 'page' === get_option( 'show_on_front' ) || get_page_by_path( 'accueil' ) ) {
		return;
	}
	ob_start();
	include get_theme_file_path( 'patterns/page-accueil.php' );
	$contenu = ob_get_clean();

	$page_id = wp_insert_post( array(
		'post_type'    => 'page',
		'post_status'  => 'publish',
		'post_title'   => 'Accueil',
		'post_name'    => 'accueil',
		'post_content' => $contenu,
		'page_template' => 'page-sections',
	) );
	if ( $page_id && ! is_wp_error( $page_id ) ) {
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', $page_id );
	}
} );
