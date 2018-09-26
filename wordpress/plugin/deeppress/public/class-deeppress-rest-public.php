<?php

class DeepPress_Rest_Public
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
    public function __construct($plugin_name, $version)
    {
        $this->plugin_name = $plugin_name;
        $this->version = $version;
        $this->namespace = $this->plugin_name.'/v'.intval($this->version);
    }

    /**
     * Add the endpoints to the API
     */
    public function add_api_routes()
    {
        register_rest_route($this->namespace, 'records', [
            'methods' => 'GET',
            'callback' => array($this, 'get_records'),
            'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
        ]);

        register_rest_route($this->namespace, 'records', [
            'methods' => 'POST',
            'callback' => array($this, 'add_record'),
            'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
        ]);


        register_rest_route($this->namespace, 'records/(?P<id>\d+)', array(
            'methods' => 'POST',
            'callback' => array($this, 'update_record'),
            'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
        ));

	    register_rest_route($this->namespace, 'records/(?P<id>\d+)/trained', array(
		    'methods' => 'POST',
		    'callback' => array($this, 'mark_trained'),
            'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
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
     * Get the records
     *
     * @param [type] $request [description]
     *
     * @return [type] [description]
     */
    public function get_records($request)
    {
        global $wpdb;
        $per_page = 10;
        $orderby = (!empty($request['orderby'])) ? $request['orderby'] : 'created_at'; //If no sort, default to title
        $order = (!empty($request['order'])) ? $request['order'] : 'desc'; //If no order, default to asc
        $current_page = (!empty($request['page'])) ? intval($request['page']) : 1; //If no order, default to asc
        $per_page = (!empty($request['per_page'])) ? intval($request['per_page']) : $per_page;
         
        $table_name = $wpdb->prefix . "deeppress";

        
        
        
        /**
         * The WP_List_Table class does not handle pagination for us, so we need
         * to ensure that the data is trimmed to only the current page. We can use
         * array_slice() to 
         */
        //$data = array_slice($data,(($current_page-1)*$per_page),$per_page);
	    $query_args = array();
        $where = array();
        if (isset($_REQUEST['group_id']) && $_REQUEST['group_id'] !== "all") {
            $where[] = "group_id = %s ";
            $query_args[] = $_REQUEST['group_id'];
        }
        if (isset($_REQUEST['start_time']) && $_REQUEST['start_time'] !== "") {
            $where[] = "created_at >= %s ";
            $query_args[] = $_REQUEST['start_time'];
        }
        if (isset($_REQUEST['end_time']) && $_REQUEST['end_time'] !== "") {
            $where[] = "created_at <= %s";
            $query_args[] = $_REQUEST['end_time'];
        }

	    if (isset($_REQUEST['processed']) && $_REQUEST['processed'] !== "") {
		    $where[] = "processed = %d";
		    $query_args[] = intval($_REQUEST['processed']);
	    }

	    if (isset($_REQUEST['annotated']) && $_REQUEST['annotated'] !== "") {
		    $where[] = "annotated = %d";
		    $query_args[] = intval($_REQUEST['annotated']);
	    }

	    if (isset($_REQUEST['trained']) && $_REQUEST['trained'] !== "") {
		    $where[] = "trained = %d";
		    $query_args[] = intval($_REQUEST['trained']);
	    }

        $where_cmd = "";

        if (sizeof($where) > 0) {
        	$where_cmd = "WHERE ". implode(" AND ", $where);
        }

        // Total records
        $total_items = $wpdb->get_var( $wpdb->prepare("SELECT COUNT(*) FROM $table_name $where_cmd", $query_args) );

        $query_args[] = $per_page;
        $query_args[] = ($current_page-1)*$per_page;

        $query = $wpdb->prepare("SELECT * FROM $table_name $where_cmd ORDER BY $orderby $order LIMIT %d OFFSET %d", $query_args);
		// return $query;
        $result = $wpdb->get_results( $query,ARRAY_A
        );

	    foreach ($result as &$d)
	    {
		    $pos =  strpos($d['image'], "/wp-content");
		    $d['image'] = substr($d['image'], $pos);
	    }

        $data = array('data' => $result, 'total' => intval($total_items), 'page' => $current_page, 'per_page' => $per_page);


        $response = new WP_REST_Response( $data );
        return $response;
    }

    public function add_record($data)
    {
        global $wpdb;
        $response = new WP_REST_Response( $this->save_record($data) );
        return $response;
       
    }

    public function update_record($data)
    {
        global $wpdb;
        $id = $data['id'];

        $data =  $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress WHERE id = $id", ARRAY_A );

        if ( null !== $data ) {
            $response = new WP_REST_Response( $this->save_record($data, $id) );
            return $response;
        } else {
            return new WP_Error(
                'record_not_found',
                "Record not found",
                array(
                    'status' => 403,
                )
            );
        } 
    }

    /**
     * Filter to hook the rest_pre_dispatch, if the is an error in the request
     * send it, if there is no error just continue with the current request.
     *
     * @param $request
     */
    public function rest_pre_dispatch($request)
    {
        if (is_wp_error($this->jwt_error)) {
            return $this->jwt_error;
        }
        return $request;
    }

    private function save_record($request, $id=null) {
        $upload_overrides = array( 
        	'test_form' => false
        );
        
        global $wpdb;
        //$wpdb->print_error();
        
        if ( ! function_exists( 'wp_handle_upload' ) ) {
            require_once( ABSPATH . 'wp-admin/includes/file.php' );
        }
        
        $wpdb->show_errors();
        $data = array();

        if (isset($_POST['count']))
            $data['count'] = intval($_POST['count']);

        if (isset($_POST['group_id']))
            $data['group_id'] = $_POST['group_id'];

        if (isset($_POST['created_at']))
            $data['created_at'] = $_POST['created_at'];

	    if (isset($_POST['remarks']))
		    $data['remarks'] = $_POST['remarks'];

	    if (isset($_POST['detections']))
		    $data['detections'] = $_POST['detections'];

	    if (isset($_POST['batt']))
		    $data['batt'] = $_POST['batt'];

	    if (isset($_POST['processed']))
		    $data['processed'] = $_POST['processed'] == 0 ? false : true;

        if (isset($_FILES['image'])) {
            $uploadedfile = $_FILES['image'];
            $movefile = wp_handle_upload( $uploadedfile, $upload_overrides );

            if ( $movefile && ! isset( $movefile['error'] ) ) {
                $data['image'] = $movefile['url'];
                $data['image_file'] = $movefile['file'];
            } else {
                echo $movefile['error'];
            }
        }

        if (isset($_FILES['processed_image'])) {
            $uploadedfile = $_FILES['processed_image'];
            $movefile = wp_handle_upload( $uploadedfile, $upload_overrides );

            if ( $movefile && ! isset( $movefile['error'] ) ) {
                $data['processed_image'] = $movefile['url'];
                $data['processed_image_file'] = $movefile['file'];
                if(isset($_POST['processed']) && $_POST['processed'] == 1) {
                	$data['processed'] = true;
                }
            } else {
                //echo $movefile['error'];
            }
        }

        if (isset($id)) {
            return $wpdb->update($wpdb->prefix . 'deeppress', $data, array('id' => $id));
        } else 
            $result = $wpdb->insert($wpdb->prefix . 'deeppress', $data);
            return $result;
    }

    public function mark_trained($request) {
    	$ids = $request['ids'];
	    global $wpdb;

	    if ( is_array($ids) ) {
	    	$ids = '('. implode(', ', $ids) . ')';
	    } else {
	    	$ids = '(' . $ids . ')';
	    }

	    $data =  $wpdb->query( "UPDATE ". $wpdb->prefix . "deeppress SET trained = True WHERE id in $ids", ARRAY_A );

	    if ( null !== $data ) {
		    $response = new WP_REST_Response();
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
}