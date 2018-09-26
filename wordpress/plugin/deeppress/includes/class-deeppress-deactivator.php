<?php

/**
 * Fired during plugin deactivation
 *
 * @link       http://example.com
 * @since      1.0.0
 *
 * @package    DeepPress
 * @subpackage DeepPress/includes
 */

/**
 * Fired during plugin deactivation.
 *
 * This class defines all code necessary to run during the plugin's deactivation.
 *
 * @since      1.0.0
 * @package    DeepPress
 * @subpackage DeepPress/includes
 * @author     Gopal Lal <gopal@baseapp.com>
 */
class DeepPress_Deactivator {

	/**
	 * Short Description. (use period)
	 *
	 * Long Description.
	 *
	 * @since    1.0.0
	 */
	public static function deactivate() {
		return;
		global $wpdb, $dp_modules;

   		foreach ($dp_modules as $module => $details) {
		    $table_name = $wpdb->prefix . $module;
		    $wpdb->query("DROP TABLE $table_name");
	    }
	}

}
