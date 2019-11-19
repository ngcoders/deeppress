<?php

/**
 * The file that defines the core plugin class
 *
 * A class definition that includes attributes and functions used across both the
 * public-facing side of the site and the admin area.
 *
 * @link       http://example.com
 * @since      1.0.0
 *
 * @package    DeepPress
 * @subpackage DeepPress/includes
 */

/**
 * The core plugin class.
 *
 * This is used to define internationalization, admin-specific hooks, and
 * public-facing site hooks.
 *
 * Also maintains the unique identifier of this plugin as well as the current
 * version of the plugin.
 *
 * @since      1.0.0
 * @package    DeepPress
 * @subpackage DeepPress/includes
 * @author     Gopal Lal<gopal@baseapp.com>
 */
class DeepPress {

	/**
	 * The loader that's responsible for maintaining and registering all hooks that power
	 * the plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      DeepPress_Loader    $loader    Maintains and registers all hooks for the plugin.
	 */
	protected $loader;

	/**
	 * The unique identifier of this plugin.
	 *
	 * @since    1.0.0
	 * @access   protected
	 * @var      string    $plugin_name    The string used to uniquely identify this plugin.
	 */
	protected $plugin_name;

	protected $version;

	public function __construct() {
		if ( defined( 'DEEPPRESS_VERSION' ) ) {
			$this->version = DEEPPRESS_VERSION;
		} else {
			$this->version = '1.0.0';
		}
		$this->plugin_name = 'deeppress';

		$this->load_dependencies();
		$this->set_locale();
		$this->define_admin_hooks();
		$this->define_public_hooks();
		$this->load_fields();

	}

	public function init_actions() {
		// register acf styles

	}

	private function load_dependencies() {

		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/class-deeppress-loader.php';

		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/class-deeppress-i18n.php';

		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-deeppress-admin.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-deeppress-admin-ajax.php';

		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'public/class-deeppress-public.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'public/class-deeppress-rest-public.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'public/class-deeppress-rest-classification.php';
		// REST For Modules
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'public/class-deeppress-rest-modules.php';

		$this->loader = new DeepPress_Loader();

	}

	/**
	 * Define the locale for this plugin for internationalization.
	 *
	 * Uses the DeepPress_i18n class in order to set the domain and to register the hook
	 * with WordPress.
	 *
	 * @since    1.0.0
	 * @access   private
	 */
	private function set_locale() {

		$plugin_i18n = new DeepPress_i18n();

		$this->loader->add_action( 'plugins_loaded', $plugin_i18n, 'load_plugin_textdomain' );

	}

	private function define_admin_hooks() {

		$plugin_admin = new DeepPress_Admin( $this->get_plugin_name(), $this->get_version() );

		$this->loader->add_action( 'admin_enqueue_scripts', $plugin_admin, 'enqueue_styles' );
		$this->loader->add_action( 'admin_enqueue_scripts', $plugin_admin, 'enqueue_scripts' );
		$this->loader->add_action( 'admin_menu', $plugin_admin, 'add_menu_page' );
		$this->loader->add_action( 'deeppress_save_record', $plugin_admin, 'save_record' );
		$this->loader->add_action( 'wp_ajax_deeppress_save_annotation', $plugin_admin, 'save_annotation' );
		$this->loader->add_action( 'admin_init', $plugin_admin, 'admin_init_actions' );
		$this->loader->add_action( 'init', $plugin_admin, 'init_actions' );

		// Ajax
		$plugin_ajax = new DeepPress_Admin_Ajax( $this->get_plugin_name(), $this->get_version() );
		$this->loader->add_action( 'wp_ajax_dp_get_models', $plugin_ajax, 'get_models' );
		$this->loader->add_action( 'wp_ajax_dp_start_training', $plugin_ajax, 'start_training' );
	}

	private function define_public_hooks() {

		$plugin_public = new DeepPress_Public( $this->get_plugin_name(), $this->get_version() );

		$this->loader->add_action( 'wp_enqueue_scripts', $plugin_public, 'enqueue_styles' );
		$this->loader->add_action( 'wp_enqueue_scripts', $plugin_public, 'enqueue_scripts' );
		$this->loader->add_action( 'init', $plugin_public, 'add_init_actions' );
		$this->loader->add_filter( 'upload_dir', $plugin_public, 'change_upload_dir' );
		$this->loader->add_filter( 'determine_current_user', $plugin_public, 'json_basic_auth_handler', 20 );
		$this->loader->add_filter( 'rest_authentication_errors', $plugin_public, 'json_basic_auth_error' );

		
		$rest_public = new DeepPress_Rest_Public($this->get_plugin_name(), $this->get_version());
		$this->loader->add_action('rest_api_init', $rest_public, 'add_api_routes');

		$rest_classification = new DeepPress_Rest_Classification($this->get_plugin_name(), $this->get_version());
		$this->loader->add_action('rest_api_init', $rest_classification, 'add_api_routes');

		global $dp_modules;
		foreach ($dp_modules as $key => $value) {			
			$rest_modules = new DeepPress_Rest_Modules($this->get_plugin_name(), $this->get_version(), $key, $value);
			$this->loader->add_action('rest_api_init', $rest_modules , 'add_api_routes');
		}

		//$this->loader->add_filter('determine_current_user', $rest_public, 'determine_current_user', 10);
        //$this->loader->add_filter( 'rest_pre_dispatch', $rest_public, 'rest_pre_dispatch', 10, 2 );
		$this->loader->add_action( 'init', $this, 'init_actions' );

	}

	public function run() {
		$this->loader->run();
	}

	public function get_plugin_name() {
		return $this->plugin_name;
	}

	public function get_loader() {
		return $this->loader;
	}

	public function get_version() {
		return $this->version;
	}

	private function load_fields() {
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/input.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/functions.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/_functions.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/class-ba-fields-base.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/text.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/select.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/checkbox.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/email.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/image.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/file.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/number.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/textarea.php';
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'includes/fields/true_false.php';
	}

}
