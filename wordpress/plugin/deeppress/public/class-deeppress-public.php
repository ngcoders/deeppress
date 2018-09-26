<?php

/**
 * The public-facing functionality of the plugin.
 *
 * @link       http://example.com
 * @since      1.0.0
 *
 * @package    DeepPress
 * @subpackage DeepPress/public
 */

/**
 * The public-facing functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the public-facing stylesheet and JavaScript.
 *
 * @package    DeepPress
 * @subpackage DeepPress/public
 * @author     Gopal Lal <gopal@baseapp.com>
 */
class DeepPress_Public {

	/**
	 * The ID of this plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 * @var      string    $plugin_name    The ID of this plugin.
	 */
	private $plugin_name;

	/**
	 * The version of this plugin.
	 *
	 * @since    1.0.0
	 * @access   private
	 * @var      string    $version    The current version of this plugin.
	 */
	private $version;

	/**
	 * Initialize the class and set its properties.
	 *
	 * @since    1.0.0
	 * @param      string    $plugin_name       The name of the plugin.
	 * @param      string    $version    The version of this plugin.
	 */
	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;

	}

	/**
	 * Register the stylesheets for the public-facing side of the site.
	 *
	 * @since    1.0.0
	 */
	public function enqueue_styles() {

		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'css/deeppress-public.css', array(), $this->version, 'all' );

	}

	/**
	 * Register the JavaScript for the public-facing side of the site.
	 *
	 * @since    1.0.0
	 */
	public function enqueue_scripts() {
		wp_enqueue_script( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'js/deeppress-public.js', array( 'jquery' ), $this->version, false );

	}

	public function change_upload_dir($uploads) {
		$subdir = date('/d/H');
		$uploads['path'] = $uploads['path'] . $subdir;
		$uploads['url'] = $uploads['url'] . $subdir;
		$uploads['subdir'] = $uploads['subdir'] . $subdir;
		return $uploads;
	}

	public function add_init_actions() {
		$styles = array(
			'ba'				=>  plugin_dir_url( __FILE__ )  . 'css/ba.css',
			'ba-field-group'	=>  plugin_dir_url( __FILE__ )  . 'ss/field-group.css',
			'ba-global'		=>  plugin_dir_url( __FILE__ )  . 'css/global.css',
			'ba-input'			=>  plugin_dir_url( __FILE__ )  . 'css/input.css',
			//'ba-datepicker'	=> $this->settings['dir'] . 'core/fields/date_picker/style.date_picker.css',
		);

		foreach( $styles as $k => $v )
		{
			wp_register_style( $k, $v, false, $this->version );
		}
	}

	public function json_basic_auth_handler( $user ) {
		global $wp_json_basic_auth_error;
		$wp_json_basic_auth_error = null;
		// Don't authenticate twice
		if ( ! empty( $user ) ) {
			return $user;
		}
		// Check that we're trying to authenticate
		if ( !isset( $_SERVER['PHP_AUTH_USER'] ) ) {
			return $user;
		}
		$username = $_SERVER['PHP_AUTH_USER'];
		$password = $_SERVER['PHP_AUTH_PW'];
		/**
		 * In multi-site, wp_authenticate_spam_check filter is run on authentication. This filter calls
		 * get_currentuserinfo which in turn calls the determine_current_user filter. This leads to infinite
		 * recursion and a stack overflow unless the current function is removed from the determine_current_user
		 * filter during authentication.
		 */
		remove_filter( 'determine_current_user', 'json_basic_auth_handler', 20 );
		$user = wp_authenticate( $username, $password );
		add_filter( 'determine_current_user', 'json_basic_auth_handler', 20 );
		if ( is_wp_error( $user ) ) {
			$wp_json_basic_auth_error = $user;
			return null;
		}
		$wp_json_basic_auth_error = true;
		return $user->ID;
	}

	public function json_basic_auth_error( $error ) {
		// Passthrough other errors
		if ( ! empty( $error ) ) {
			return $error;
		}
		global $wp_json_basic_auth_error;
		return $wp_json_basic_auth_error;
	}
}
