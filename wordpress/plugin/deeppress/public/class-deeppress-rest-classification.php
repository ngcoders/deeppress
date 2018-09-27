<?php

class DeepPress_Rest_Classification
{
    private $plugin_name;

    private $version;

    private $namespace;

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
        register_rest_route($this->namespace, 'classification', [
            'methods' => 'GET',
            'callback' => array($this, 'get_records'),
            'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
        ]);

        register_rest_route($this->namespace, 'classification', [
            'methods' => 'POST',
            'callback' => array($this, 'add_record'),
            'permission_callback' => function () {
                return current_user_can( 'edit_others_posts' );
            }
        ]);


	    register_rest_route($this->namespace, 'classification/(?P<id>\d+)/images', array(
		    'methods' => 'GET',
		    'callback' => array($this, 'get_images'),
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
         
        $table_name = $wpdb->prefix . "deeppress_classification";

        
        
        
        /**
         * The WP_List_Table class does not handle pagination for us, so we need
         * to ensure that the data is trimmed to only the current page. We can use
         * array_slice() to 
         */
        //$data = array_slice($data,(($current_page-1)*$per_page),$per_page);
	    $query_args = array();
        $where = array();
        if (isset($_REQUEST['category']) && $_REQUEST['category'] !== "all") {
            $where[] = "category = %s ";
            $query_args[] = $_REQUEST['category'];
        }
        
        $where_cmd = "";

        if (sizeof($where) > 0) {
        	$where_cmd = "WHERE ". implode(" AND ", $where);
        }

        // Total records
        if (sizeof($query_args) > 0)
            $total_items = $wpdb->get_var( $wpdb->prepare("SELECT COUNT(*) FROM $table_name $where_cmd", $query_args) );
        else
            $total_items = $wpdb->get_var("SELECT COUNT(*) FROM $table_name");
        
        $query_args[] = $per_page;
        $query_args[] = ($current_page-1)*$per_page;

        $query = $wpdb->prepare("SELECT * FROM $table_name $where_cmd ORDER BY $orderby $order LIMIT %d OFFSET %d", $query_args);
		// return $query;
        $result = $wpdb->get_results( $query,ARRAY_A );

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
        $data = array(
			'category' => $_POST['category']
		);

		if (isset($_FILES['file'])) {
			$uploadedfile = $_FILES['file'];
			$upload_overrides = array( 'test_form' => false );
			$movefile = wp_handle_upload( $uploadedfile, $upload_overrides );
			var_dump($movefile);

			if ( $movefile && ! isset( $movefile['error'] ) ) {
				if ( $movefile['type'] != "application/zip") {
					return;
				}
				$wp_up_dir = wp_upload_dir();
				$new_location = $wp_up_dir['path'] . '/'. $data['category'] . '_' . time();
				mkdir($new_location);
				$zip_file = $movefile['file'];
				WP_Filesystem();
				$unzipfile = unzip_file( $zip_file, $new_location);
   
				if ( is_wp_error( $unzipfile ) ) {
						var_dump($unzipfile);
						echo 'There was an error unzipping the file.'; 
						unlink($zip_file);
						return;
				} 
				unlink($zip_file);
			    $data['dir_path'] = $new_location;
			} else {
			    echo $movefile['error'];
			}
		}

		$result = $wpdb->insert($wpdb->prefix . 'deeppress_classification', $data);
	    
            return $result;
    }

    public function listFolderFiles($dir){
        $ffs = scandir($dir);
        $all = [];
        unset($ffs[array_search('.', $ffs, true)]);
        unset($ffs[array_search('..', $ffs, true)]);
    
        // prevent empty ordered elements
        if (count($ffs) < 1)
            return;
    
        // echo '<ol>';
        foreach($ffs as $ff){
            // echo '<li>'.$ff;
            if(is_dir($dir.'/'.$ff)) {
                $all = array_merge($all, $this->listFolderFiles($dir.'/'.$ff)) ;   
            } else {
                $pos =  strpos($dir.'/'.$ff, "/wp-content");
		        $all[] = substr($dir.'/'.$ff, $pos);
            }
        }
        // echo '</ol>';
        return $all;
    }

    public function get_images($request) {
    	$id = $request['id'];
	    global $wpdb;

	    $data =  $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress_classification WHERE id = $id", ARRAY_A );

	    if ( null !== $data ) {
		    $response = new WP_REST_Response(array('data' => $this->listFolderFiles($data['dir_path'])));
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