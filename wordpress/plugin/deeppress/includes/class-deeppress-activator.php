<?php
/**
 * Fired during plugin activation
 *
 * @link       http://example.com
 * @since      1.0.0
 *
 * @package    DeepPress
 * @subpackage DeepPress/includes
 */
/**
 * Fired during plugin activation.
 *
 * This class defines all code necessary to run during the plugin's activation.
 *
 * @since      1.0.0
 * @package    DeepPress
 * @subpackage DeepPress/includes
 * @author     Gopal Lal <gopal@baseapp.com>
 */
class DeepPress_Activator {
	/**
	 * Activate Plugin.
	 *
	 * Create Database tables.
	 *
	 * @since    1.0.0
	 */
	public static function activate() {
		self::create_table();
		// add_option('deeppress_auth_key', '255', '', 'yes');
	}

	public static function create_table() {
		global $wpdb, $dp_modules;
		$wpdb->show_errors();

   		$table_name = $wpdb->prefix . "deeppress";

   		$charset_collate = $wpdb->get_charset_collate();

		$sql = "CREATE TABLE $table_name (
		  id mediumint(9) NOT NULL AUTO_INCREMENT,
		  group_id tinytext NOT NULL,
		  image text,
		  image_file text,
		  box text,
		  annotated BOOLEAN DEFAULT FALSE,
		  trained BOOLEAN DEFAULT FALSE,
		  annotated_by bigint DEFAULT 0,
		  annotated_at TIMESTAMP NULL DEFAULT NULL,
		  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
		  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		  PRIMARY KEY  (id)
		) $charset_collate;";

		$classification_table_name = $wpdb->prefix . "deeppress_classification";

		$classification_sql = "CREATE TABLE $classification_table_name (
		  id mediumint(9) NOT NULL AUTO_INCREMENT,
		  category VARCHAR(255) NOT NULL,
		  dir_path text,
		  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
		  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		  PRIMARY KEY  (id)
		) $charset_collate;";

		require_once( ABSPATH . 'wp-admin/includes/upgrade.php' );
		dbDelta( $sql );
		dbDelta($classification_sql);
		//dbDelta( $sql_modules );
		foreach ($dp_modules as $name => $module) {
			$mq = self::get_query($module);
			$module_table = $wpdb->prefix . $name;
			$q = "CREATE TABLE $module_table ( $mq ) $charset_collate; ";
			dbDelta($q);
		}

		// if ($wpdb->query($sql) === false) {
		// 	echo "Failed to create the table";
		// }
	}

	public static function get_query($module) {
		$fields = $module['fields'];
		$q      = "";
		if ( ! in_array( 'id', array_keys( $fields ) ) ) {
			$q .= " id mediumint(9) NOT NULL AUTO_INCREMENT, ";
		}
		foreach ( $fields as $f ) {
			$q .= $f['name'] . " ";
			if (isset($f['unique']) && $f['unique']) {
				$q .= self::data_type($f['type'], true) . " NOT NULL UNIQUE";
			} else {
				$q .= self::data_type($f['type'], false);
			}
			$q .= ", ";
		}

		$q .= "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
		  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		  PRIMARY KEY  (id)";

		return $q;
	}

	public static function data_type($t, $unique) {
		switch ($t) {
			case 'text':
			case 'file':
			case 'image':
				if ($unique)
					return 'VARCHAR(255)';
				return 'TEXT';
			case 'number':
				return 'INT';
			case 'boolean':
				return 'BOOLEAN';
			default:
				if ($unique)
					return 'VARCHAR(255)';
				return 'TEXT';
		}
	}

}