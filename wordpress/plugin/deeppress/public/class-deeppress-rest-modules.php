<?php

class DeepPress_Rest_Modules
{
	/**
	 * The ID of this plugin.
	 *
	 * @since    1.0.0
	 *
	 * @var string The ID of this plugin.
	 */
	private $plugin_name;

	/**
	 * The version of this plugin.
	 *
	 * @since    1.0.0
	 *
	 * @var string The current version of this plugin.
	 */
	private $version;

	/**
	 * The namespace to add to the api calls.
	 *
	 * @var string The namespace to add to the api call
	 */
	private $namespace;

	/**
	 * Initialize the class and set its properties.
	 *
	 * @since    1.0.0
	 *
	 * @param string $plugin_name The name of the plugin.
	 * @param string $version     The version of this plugin.
	 */
	public function __construct($plugin_name, $version, $module_name, $module_data)
	{
		$this->plugin_name = $plugin_name;
		$this->version = $version;
		$this->namespace = $this->plugin_name.'/v'.intval($this->version);
		$this->module_name = $module_name;
	}

	/**
	 * Add the endpoints to the API
	 */
	public function add_api_routes()
	{
		register_rest_route($this->namespace, $this->module_name, [
			'methods'           => 'GET',
			'callback'          => array($this, 'get_items'),
			'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
		]);

		register_rest_route($this->namespace, $this->module_name, [
			'methods'           => 'POST',
			'callback'          => array($this, 'create_item'),
			'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
		]);


		register_rest_route($this->namespace, $this->module_name.'/(?P<id>\d+)', array(
			array(
				'methods'       =>  WP_REST_Server::READABLE,
				'callback'      =>  array($this, 'get_item'),
				'permission_callback' => function () {
                	return current_user_can( 'edit_others_posts' );
            	}
			),
			array(
				'methods'       =>  'POST',
				'callback'      =>  array($this, 'update_record'),
				'permission_callback' => function () {
                	return current_user_can( 'edit_others_posts' );
            	}
			)
		));
	}

	/**
	 * Add CORs suppot to the request.
	 */
	public function add_cors_support()
	{
		$enable_cors = defined('JWT_AUTH_CORS_ENABLE') ? JWT_AUTH_CORS_ENABLE : false;
		if ($enable_cors) {
			$headers = apply_filters('jwt_auth_cors_allow_headers', 'Access-Control-Allow-Headers, Content-Type, Authorization');
			header(sprintf('Access-Control-Allow-Headers: %s', $headers));
		}
	}

	/**
	 * Get the user and password in the request body and generate a JWT
	 *
	 * @param [type] $request [description]
	 *
	 * @return [type] [description]
	 */
	public function get_items($request)
	{
		global $wpdb, $dp_modules;

		$module_name = $this->module_name;

		if (! in_array($module_name, array_keys($dp_modules))) {
			return new WP_Error(
				'module_not_found',
				"Module not found",
				array(
					'status' => 404,
				)
			);
		}

		$per_page = 10;
		$orderby = (!empty($request['orderby'])) ? $request['orderby'] : 'created_at'; //If no sort, default to title
		$order = (!empty($request['order'])) ? $request['order'] : 'desc'; //If no order, default to asc
		$current_page = (!empty($request['page'])) ? intval($request['page']) : 1; //If no order, default to asc
		$per_page = (!empty($request['per_page'])) ? intval($request['per_page']) : $per_page;

		$table_name = $wpdb->prefix . $module_name;




		/**
		 * The WP_List_Table class does not handle pagination for us, so we need
		 * to ensure that the data is trimmed to only the current page. We can use
		 * array_slice() to
		 */
		//$data = array_slice($data,(($current_page-1)*$per_page),$per_page);
		$query_args = array();
		$where = array();
		if (isset($_REQUEST['start_time']) && $_REQUEST['start_time'] !== "") {
			// $where[] = "created_at >= '".$_REQUEST['start_time']."'";
			$where[] = "created_at >= %s ";
			$query_args[] = $_REQUEST['start_time'];
		}
		if (isset($_REQUEST['end_time']) && $_REQUEST['end_time'] !== "") {
			//$where[] = "created_at <= '".$_REQUEST['end_time']."'";
			$where[] = "created_at <= %s";
			$query_args[] = $_REQUEST['end_time'];
		}

		$where_cmd = "";

		if (sizeof($where) > 0) {
			$where_cmd = "WHERE ". implode(" AND ", $where);
			$total_items = $wpdb->get_var( $wpdb->prepare("SELECT COUNT(*) FROM $table_name $where_cmd", $query_args) );
		} else {
			$total_items = $wpdb->get_var( "SELECT COUNT(*) FROM $table_name");
		}

		// Total records

		$query_args[] = $per_page;
		$query_args[] = ($current_page-1)*$per_page;

		$query = $wpdb->prepare("SELECT * FROM $table_name $where_cmd ORDER BY $orderby $order LIMIT %d OFFSET %d", $query_args);
		// return $query;
		$result = $wpdb->get_results( $query,ARRAY_A
		);

		$fields = $dp_modules[ $module_name ]['fields'];

		foreach ($result as &$item){
			foreach ( $fields as $k => $v ) {
				$v = apply_filters('dp/load_field_defaults', $v);
				$item[$k] = apply_filters('dp/format_value_for_api', $item[$k], $item['id'], $v);
			}
		}

		$data = array('data' => $result, 'total' => intval($total_items), 'page' => $current_page, 'per_page' => $per_page);
		$response = new WP_REST_Response( $data );
		return $response;
	}

	public function create_item($request)
	{
		global $wpdb, $dp_modules;

		$module_name = $this->module_name;

		if (! in_array($module_name, array_keys($dp_modules))) {
			return new WP_Error(
				'module_not_found',
				"Module not found",
				array(
					'status' => 404,
				)
			);
		}
		$response = new WP_REST_Response( $this->save_record($request, $module_name) );
		return $response;

	}

	public function get_item( $request ) {
		$module_name = $this->module_name;
		$id = $request['id'];

		global $wpdb, $dp_modules;

		if (! in_array($module_name, array_keys($dp_modules))) {
			return new WP_Error(
				'module_not_found',
				"Module not found",
				array(
					'status' => 404,
				)
			);
		}

		return $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . $module_name . " WHERE id = $id", ARRAY_A );
	}

	public function update_record($request)
	{
		global $wpdb, $dp_modules;

		$module_name = $this->module_name;

		if (! in_array($module_name, array_keys($dp_modules))) {
			return new WP_Error(
				'module_not_found',
				"Module not found",
				array(
					'status' => 404,
				)
			);
		}
		$id = $request['id'];

		$data =  $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . $module_name ." WHERE id = $id", ARRAY_A );

		if ( null !== $data ) {
			$response = new WP_REST_Response( $this->save_record($request, $module_name, $id) );
			return $response;
		} else {
			return new WP_Error(
				'record_not_found',
				"Record not found",
				array(
					'status' => 404,
				)
			);
		}
	}

	private function save_record($request, $module_name, $id=null) {
		global $wpdb, $dp_modules;
		// $wpdb->print_error();

		// $wpdb->show_errors();

		$fields = $dp_modules[ $module_name ]['fields'];
		$data   = array();
		foreach ( $fields as $k => $v ) {
			if ( isset( $_POST[ $k ] ) ) {
				$data[ $k ] = $_POST[ $k ];
			}
		}


		if ( isset( $id ) ) {
			$result = $wpdb->update( $wpdb->prefix . $module_name, $data, array( 'id' => $id ) );
		} else {
			$result = $wpdb->insert( $wpdb->prefix . $module_name, $data );
		}

		if ( false === $result ) {
			//var_dump("failed to save");
			//exit();
		}
		return $result;
	}
}