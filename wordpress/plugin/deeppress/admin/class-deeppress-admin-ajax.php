<?php
/**
 * The admin-ajax-specific functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the admin-specific stylesheet and JavaScript.
 *
 * @package    DeepPress
 * @subpackage DeepPress/admin
 * @author     Gopal Lal <gopal@baseapp.com>
 */

class DeepPress_Admin_Ajax {

	private $plugin_name;
	private $version;

	private $messages;

	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;
    }

    public function get_models(){
		global $wpdb;
		$type = $_POST['type'];
		if($type === 'classification')
			$type = 'classifier';
		else
			$type = 'detector';
		$rows = $wpdb->get_results( "SELECT * FROM ". $wpdb->prefix . "dp_models WHERE model_type = '" . $type . "'LIMIT 100", ARRAY_A );
		$response = array(
			'what'=>'result',
			'action'=>'get_models' . $_POST['model_type'],
			'data'=>$rows
		);
		ob_clean();
		wp_send_json($response);
		wp_die();
    }

    public function start_training(){
        global $wpdb;
        $args = array(
            'headers' => array(
                'Authorization' => 'Basic ' . base64_encode( get_option('deeppress_remote_username') . ':' . get_option('deeppress_remote_password') )
            )
        );
        $response = wp_remote_post(get_option('deeppress_remote_url') . '/training/start', $args);
        $response = array(
            'what'=>'result',
            'action'=>'start_training',
            'data'=> ['status' => wp_remote_retrieve_response_code( $response )]
        );
        ob_clean();
        wp_send_json($response);
        wp_die();
    }
}