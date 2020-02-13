<?php
/**
 * The admin-specific functionality of the plugin.
 *
 * Defines the plugin name, version, and two examples hooks for how to
 * enqueue the admin-specific stylesheet and JavaScript.
 *
 * @package    DeepPress
 * @subpackage DeepPress/admin
 * @author     Gopal Lal <gopal@baseapp.com>
 */



class DeepPress_Admin {

	private $plugin_name;
	private $version;
	private $redirect_to;
	private $modules;

	private $messages;

	public function __construct( $plugin_name, $version ) {

		$this->plugin_name = $plugin_name;
		$this->version = $version;
		$this->redirect_to = null;
		global $dp_modules;
		$this->modules = $dp_modules;

		$this->messages = array(
            '10'    =>  array(
                    'message'   =>  'Record created',
                    'type'      => 'success'
                ),
            '11'    => array(
                    'message'   => 'Record Updated',
                    'type'      => 'success'
            ),
            '12'    => array(
	            'message'   => 'Failed',
	            'type'      => 'error'
            )
        );
	}

	/**
	 * Register the stylesheets for the admin area.
	 *
	 */
	public function enqueue_styles() {
		wp_enqueue_style( $this->plugin_name, plugin_dir_url( __FILE__ ) . 'css/deeppress-admin.css', array(), $this->version, 'all' );
		wp_enqueue_style( 
			$this->plugin_name.'-imageview', plugin_dir_url( __FILE__ ) . 'css/jquery.imageview.css', 
			array(), 
			$this->version, 'all' 
		);
		wp_enqueue_style( 
			$this->plugin_name.'-annotorious', plugin_dir_url( __FILE__ ) . 'css/jquery.selectareas.css', 
			array(), 
			$this->version, 'all' 
		);
		wp_enqueue_style(
			$this->plugin_name.'-lightgallery', plugin_dir_url( __FILE__ ) . 'css/lightgallery.min.css',
			array(),
			$this->version, 'all'
		);

	}

	public function init_actions(){

        $this->save_data();
	}

	/**
	 * Register the JavaScript for the admin area.
	 *
	 */
	public function enqueue_scripts() {
		wp_enqueue_script( 
			$this->plugin_name, plugin_dir_url( __FILE__ ) . 'js/deeppress-admin.js',
			array( 'jquery' ), 
			$this->version, true 
		);
		wp_enqueue_script( 
			$this->plugin_name.'-imageview', plugin_dir_url( __FILE__ ) . 'js/jquery.imageview.js', 
			array( 'jquery' ), 
			$this->version, false 
		);
		wp_enqueue_script( 
			$this->plugin_name.'-annotorious', plugin_dir_url( __FILE__ ) . 'js/jquery.selectareas.js',
			array( 'jquery' ), 
			$this->version, false 
		);
		wp_enqueue_script(
			$this->plugin_name.'-input', plugin_dir_url( __FILE__ ) . 'js/input.js',
			array( 'jquery' ),
			$this->version, false
		);
		wp_enqueue_script(
			$this->plugin_name.'-lightgallery', plugin_dir_url( __FILE__ ) . 'js/lightgallery.min.js',
			array( 'jquery' ),
			$this->version, false
		);
		/*wp_enqueue_script(
			$this->plugin_name.'-dropzone', plugin_dir_url( __FILE__ ) . 'js/dropzone.js',
			array( 'jquery' ),
			$this->version, false
		);*/
		// Localize the script with new data
		$config_array = array(
			'remote_url' => get_option('deeppress_remote_url'),
			'remote_username' => get_option('deeppress_remote_username'),
			'remote_password' => get_option('deeppress_remote_password')
		);
		wp_localize_script( $this->plugin_name, 'deeppress', $config_array );
	}

	public function admin_init_actions(){
		// add_option( 'deeppress_remote_url', 'This is my option value.');
   		register_setting( 'deeppress_options_group', 'remote_url', 'myplugin_callback' );
		$this->process_actions();
	}

	public function add_menu_page() {
		$this->admin_page = add_menu_page(
			"DeepPress",
			"DeepPress",
			'edit_posts',
			'deeppress',
			array($this, 'menu_page')
		);

		add_submenu_page('deeppress',
			'Detection',
			'Detection',
			'edit_others_posts',
			'deeppress',
			array($this, 'menu_page')
		);

		add_submenu_page('deeppress',
			'Classification',
			'Classification',
			'edit_others_posts',
			'classification',
			array($this, 'classification_page')
		);

		foreach ($this->modules as $m) {
			add_submenu_page('deeppress',
				$m['page_title'],
				$m['menu_title'],
				'edit_others_posts',
				$m['menu_slug'],
				array($this, 'module_page')
			);
		}

		add_submenu_page('deeppress',
			'Stats',
			'Stats',
			'edit_others_posts',
			'stats',
			array($this, 'stats_page')
		);

		add_submenu_page('deeppress',
			'Test',
			'Test',
			'edit_others_posts',
			'test',
			array($this, 'test_page')
		);

		add_submenu_page('deeppress',
			'Settings',
			'Settings',
			'edit_others_posts',
			'settings',
			array($this, 'options_page')
		);

		add_action("load-{$this->admin_page}",array($this,'create_help_screen'));
		// add_options_page("DeepPress Settings", "DeepPress", 'manage_options', 'deeppress_options', array($this, 'options_page'));
	}

	public function create_help_screen() {

		/**
		 * Create the WP_Screen object against your admin page handle
		 * This ensures we're working with the right admin page
		 */
		$this->admin_screen = WP_Screen::get( $this->admin_page );

		$this->admin_screen->add_help_tab(
			array(
				'title'    => 'Annotation Guide',
				'id'       => 'annotation_tab',
				'content'  => '<p>Drag the mouse and draw a rectangle around the object and the click save.</p>',
				'callback' => false
			)
		);
	}

	public function options_page() {
		if ( !current_user_can( 'manage_options' ) )  {
			wp_die( __( 'You do not have sufficient permissions to access this page.' ) );
		}
		$optionName = 'deeppress_remote_url';
		if(isset($_POST['deeppress_remote_url'])) {
			update_option($optionName, $_POST['deeppress_remote_url']);
		}
		if(isset($_POST['deeppress_remote_username'])) {
			update_option('deeppress_remote_username', $_POST['deeppress_remote_username']);
		}
		if(isset($_POST['deeppress_remote_password'])) {
			update_option('deeppress_remote_password', $_POST['deeppress_remote_password']);
		}
		?>

		<div class="wrap">
	        
	        <h1 class="wp-heading-inline">Manage DeepPress Settings</h1>
	        <div>
	        	<form id="deeppress-update-options" method="post">
					<?php settings_fields( 'deeppress_options_group' ); ?>
					
					<table class="form-table">
						<tr>
							<th scope="row"><label>Remote Host Url</label>	</th>
							<td>
								<input type="text" name="deeppress_remote_url" value="<?php echo get_option('deeppress_remote_url'); ?>">
							</td>
						</tr>
						<tr>
							<th scope="row"><label>Remote Username</label>	</th>
							<td>
								<input type="text" name="deeppress_remote_username" value="<?php echo get_option('deeppress_remote_username'); ?>">
							</td>
						</tr>
						<tr>
							<th scope="row"><label>Remote Password</label>	</th>
							<td>
								<input type="text" name="deeppress_remote_password" value="<?php echo get_option('deeppress_remote_password'); ?>">
							</td>
						</tr>
						<tr>
							<th scope="row">
							<?php  submit_button(); ?>
							</th>
						</tr>
					</table>
				</form>
	        </div>
	    </div>

		<?php
	}

	public function module_page() {
	    $page = $_REQUEST['page'];
	    $action = 'list';

	    if (isset($_REQUEST['action'])) {
	        $action = $_REQUEST['action'];
	    }

	    if (!in_array($page, array_keys($this->modules))) {
	        echo "No Module Found";
	        die();
        }

        if (isset($_REQUEST['message'])) {
	        echo '<div class="notice notice-'. $this->messages[$_REQUEST['message']]['type'].' is-dismissible"><p>';
	        echo $this->messages[$_REQUEST['message']]['message'];
	        echo '</p></div>';
        }

        $module = $this->modules[$page];

        if ("create" === $action || "edit" === $action) {
		    $this->add_page($this->modules[$page], $action);
		    return;
        }

        if ($action === 'list') {
            require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-deeppress-admin-record-table.php';

		    //Create an instance of our package class...
	        $recordsTable = new DeepPress_List_Table($page, $module);
	        //Fetch, prepare, sort, and filter our data...
	        $recordsTable->prepare_items();
	        ?>
            <div class="wrap" id="lightgallery">

                <div id="icon-users" class="icon32"><br/></div>
                <h1 class="wp-heading-inline"><?php echo($module['page_title']) ?></h1>
                <a href="<?php menu_page_url($page) ?>&action=create" class="page-title-action">Add a record</a>
                <hr class="wp-header-end">
                <!-- Forms are NOT created automatically, so you need to wrap the table in one to use features like bulk actions -->
                <form id="record-filter" method="get">
                    <!-- For plugins, we also need to ensure that the form posts back to our current page -->
                    <input type="hidden" name="page" value="<?php echo $_REQUEST['page'] ?>" />
                     <?php $recordsTable->display() ?>
                </form>
            </div>
	    <?php
        }
	}

	public function menu_page() {
	    if ( !current_user_can( 'edit_posts' ) )  {
			wp_die( __( 'You do not have sufficient permissions to access this page.' ) );
		}

		if (isset($_REQUEST['action'])) {
            $action = $_REQUEST['action'];
            if ("create" === $action || "edit" === $action) {
                $this->record_page('deeppress');
                return;
            } else if ("annotate" === $action && current_user_can( 'edit_posts' )) {
                $this->show_annotate();
                return;
            } else if ("store" === $action || "update" === $action) {
                do_action('deeppress_save_record');
            }
        }

		$this->list_records();	
	}

	public function stats_page()
    {
	    ?>
        <div class="wrap" id="lightgallery">

            <div id="icon-users" class="icon32"><br/></div>
            <h1 class="wp-heading-inline">Stats</h1>
            <hr class="wp-header-end">
            <form id="record-filter" method="get">
                <!-- For plugins, we also need to ensure that the form posts back to our current page -->
                <input type="hidden" name="page" value="<?php echo $_REQUEST['page'] ?>" />
			    <?php do_action('dp_show_deeppress_stats'); ?>
            </form>
        </div>
	    <?php

	}

	public function test_page()
	{
		$models = [];
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/partials/deeppress-admin-test-page.php';
	}
	
	/**
	 * Classification Page
	 */
	public function classification_page()
	{
		if ( !current_user_can( 'edit_posts' ) )  {
			wp_die( __( 'You do not have sufficient permissions to access this page.' ) );
		}

        if (isset($_REQUEST['action'])) {
            $action = $_REQUEST['action'];
            if ("create" === $action || "edit" === $action) {
                $this->record_page('classification');
                return;
            } else if ("store" === $action || "update" === $action) {
                $this->save_classification_record();
            }
        }
		
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-deeppress-admin-classification-table.php';
		
		//Create an instance of our package class...
	    $testListTable = new DeepPress_Classification_Table();
	    //Fetch, prepare, sort, and filter our data...
	    $testListTable->prepare_items();

	    ?>
	    <div class="wrap" id="lightgallery">
	        
	        <div id="icon-users" class="icon32"><br/></div>
	        <h1 class="wp-heading-inline">Records</h1>
	        <a href="<?php menu_page_url('classification') ?>&action=create" class="page-title-action">Add a record</a>
	        <!-- Forms are NOT created automatically, so you need to wrap the table in one to use features like bulk actions -->
            <hr class="wp-header-end">
            <form id="record-filter" method="get">
	            <!-- For plugins, we also need to ensure that the form posts back to our current page -->
	            <input type="hidden" name="page" value="<?php echo $_REQUEST['page'] ?>" />
	            <?php $testListTable->display() ?>
	        </form>
	        
	    </div>

	    <?php
	}

	protected function add_page($module, $action) {
	    if ("edit" === $action) {
	        $id = $_REQUEST['id'];
	        $record = $this->get_module_record($module['menu_slug'], $id);

	    }
		?>
        <div class="wrap">
            <div class="">
				<h1 class="wp-heading-inline"><?php echo isset($record) ? "Edit" :"Add new" ?> Record</h1>
	        <a href="<?php menu_page_url($module['menu_slug']) ?>" class="page-title-action">Back</a>
            </div>
	        <form action="" method="post" id="post">
	        <table>
	        <?php
                foreach ($module['fields'] as $f) {
                    $f = apply_filters('dp/load_field_defaults', $f);
	                if(isset($record)){
		                $f['value'] = $record[$f['name']];
		                if(isset($f['serialize']) && $f['serialize']) {
			                $f['value'] = unserialize( $f['value'] );
		                }
                    }

	                $required_class = '';
	                $required_label = '';
	                if( $f['required'] )
	                {
		                $required_class = ' required';
		                $required_label = ' <span class="required">*</span>';
	                }
	                echo '<tr id="ba-' . $f['name'] . '" class="form-field field field_type-' . $f['type'] . $required_class . ' field_key-' . $f['key'] .' data-field_name="' . $f['name'] . '" data-field_key="' . $f['name'] . '" data-field_type="' . $f['type'] . '">';
	                echo '<th valign="top" scope="row"><label for="' . $f['name'] . '">' . $f['placeholder'] . $required_label . '</label></th>';
	                echo '<td>';
	                do_action('dp/create_field', $f );

	                if($f['instructions']) echo '<p class="description">' . $f['instructions'] . '</p>';
	                echo '</td>';
	                echo '</tr>';

                }
	        wp_referer_field( true );
            ?>
            </table>

            <input type="submit" value="Save" class="btn">
            </form>
        </div>
		<?php
    }

	public function show_annotate() {
		$record = $this->get_record($_REQUEST['id']);
        $next_id = intval($record['id']) - 1;
		//var_dump($record);
		$box = json_decode(preg_replace('/\\\\"/m', '"', $record['box']), true);
		if (is_null($box)) {
		    //echo $record['remarks'];
			//$json = preg_replace('/\\\\"/m', '"', $record['detections']);
		    //var_dump($json);
			//$box = json_decode($json, true);

			//var_dump($box);
			if (is_null($box)) {
				$box = array();
			}
		}
		$box_str = array();
		foreach ($box as $rect) {
		    $obClass = isset($rect['class']) ? $rect['class'] : "person";
			array_push($box_str, '{x: '.$rect['x'].', y: '.$rect['y'].', width: '.$rect['width'].', height: '.$rect['height'].', class: "'. $obClass .'"}');
		}
		$box_str = implode(', ', $box_str);
		// $box_str = json_encode($box);

		$pos =  strpos($record['image'], "/wp-content");
		$record['image'] = substr($record['image'], $pos);

		$classes = json_encode(array_column(self::get_classes(), 'class'));

		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/partials/deeppress-admin-display-annotation.php';

	}

	public function list_records() {
		require_once plugin_dir_path( dirname( __FILE__ ) ) . 'admin/class-deeppress-admin-list-table.php';
		
		//Create an instance of our package class...
	    $testListTable = new DeepPress_List_Table();
	    //Fetch, prepare, sort, and filter our data...
	    $testListTable->prepare_items();

	    ?>
	    <div class="wrap" id="lightgallery">
	        
	        <div id="icon-users" class="icon32"><br/></div>
	        <h1 class="wp-heading-inline">Records</h1>
	        <a href="<?php menu_page_url('deeppress') ?>&action=create" class="page-title-action">Add a record</a>
	        <!-- Forms are NOT created automatically, so you need to wrap the table in one to use features like bulk actions -->
            <hr class="wp-header-end">
            <form id="record-filter" method="get">
	            <!-- For plugins, we also need to ensure that the form posts back to our current page -->
	            <input type="hidden" name="page" value="<?php echo $_REQUEST['page'] ?>" />
	            <?php $testListTable->display() ?>
	        </form>
	        
	    </div>

	    <?php
	}

	public function save_record() {
		global $wpdb;
		if ( ! function_exists( 'wp_handle_upload' ) ) {
			require_once( ABSPATH . 'wp-admin/includes/file.php' );
		}
		$wpdb->show_errors();
		$data = array(
			'group_id' => $_POST['group_id']
		);

		if (isset($_FILES['image'])) {
			$uploadedfile = $_FILES['image'];
			$upload_overrides = array( 'test_form' => false );
			$movefile = wp_handle_upload( $uploadedfile, $upload_overrides );

			if ( $movefile && ! isset( $movefile['error'] ) ) {
				if ( $movefile['type'] == "application/zip") {
					$wp_up_dir = wp_upload_dir();
					$new_location = $wp_up_dir['path'] . '/'. time();
					if(! mkdir($new_location, 0777, true))
						return;
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
					$dir = $new_location;
					$files = apply_filters('dp_images_in_dir', $dir);
					foreach($files as $f){
						$pos =  strpos($f, "/wp-content");		        		
						$data['image'] = substr($f, $pos);
						$data['image_file'] = $f;
						$result = $wpdb->insert($wpdb->prefix . 'deeppress', $data);
					}
				} else {
					$data['image'] = $movefile['url'];
					$data['image_file'] = $movefile['file'];
					$result = $wpdb->insert($wpdb->prefix . 'deeppress', $data);
					
				}
				$wpdb->show_errors();
			    
			} else {
			    echo $movefile['error'];
			}
		}

		// $result = $wpdb->insert($wpdb->prefix . 'deeppress', $data);
		
		// //$redirect_to = add_query_arg( $query, menu_page_url( 'deeppress', false ) );
		// wp_redirect(menu_page_url('deeppress'));
		// exit();
	}

	public function save_classification_record() {
		global $wpdb;
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
		
	}

	public function get_record($id) {
		global $wpdb;
		return $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress WHERE id = $id", ARRAY_A );
	}

	public function get_classes(){
        global $wpdb;
        return $wpdb->get_results( "SELECT * FROM ". $wpdb->prefix . "dp_classes ORDER BY weight DESC", ARRAY_A );

    }

	public function get_module_record($module_name, $id) {
		global $wpdb;
		return $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . $module_name . " WHERE id = $id", ARRAY_A );
	}

	public function record_page($current_page) {
		if (isset($_REQUEST['id'])) {
			// Edit a record
			$record = $this->get_record($_REQUEST['id']);
		}

		?>

			<div class="wrap">
				<h1 class="wp-heading-inline"><?php echo isset($record) ? "Edit" :"Add new" ?> Record</h1>
	        <a href="<?php menu_page_url($current_page) ?>" class="page-title-action">Back</a>
				<form id="deeppress-create-record" class="" method="post" enctype="multipart/form-data" action="<?php menu_page_url($current_page) ?>">
					<input type="hidden" name="action" value="store">
					<?php if (isset($record)) {
						echo '<input type="hidden" name="id" value="'.$record['id'].'">';
					}
					if($current_page == 'deeppress'){
					?>
					<table class="form-table">
						<?php 
							$f = array(
								'name'  =>  'group_id',
								'type'  =>  'select',
								'relative' =>  1,
								'module'    =>  'dp_groups',
								'placeholder'   =>  'Group',
								'value'     =>  isset($record)?$record['group_id']:'common',
								'choices'   => [],
								'instructions'  =>  'Group name',
								'foreign_key'   =>  'group_id'
							);
							$f = apply_filters('dp/load_field_defaults', $f);
							if(isset($record)){
								$f['value'] = $record[$f['name']];
								if(isset($f['serialize']) && $f['serialize']) {
									$f['value'] = unserialize( $f['value'] );
								}
							}
		
							$required_class = '';
							$required_label = '';
							if( $f['required'] )
							{
								$required_class = ' required';
								$required_label = ' <span class="required">*</span>';
							}
							echo '<tr id="ba-' . $f['name'] . '" class="form-field field field_type-' . $f['type'] . $required_class . ' field_key-' . $f['key'] .' data-field_name="' . $f['name'] . '" data-field_key="' . $f['name'] . '" data-field_type="' . $f['type'] . '">';
							echo '<th valign="top" scope="row"><label for="' . $f['name'] . '">' . $f['placeholder'] . $required_label . '</label></th>';
							echo '<td>';
							do_action('dp/create_field', $f );
		
							if($f['instructions']) echo '<p class="description">' . $f['instructions'] . '</p>';
							echo '</td>';
							echo '</tr>';
						?>
						<tr>
							<th scope="row">
								<label>Image</label>
							</th>
							<td>
								<?php 
									echo '<input type="file" name="image">';
									?>
							</td>
						</tr>
						<tr>
							<th scope="row">
								<button>Save</button>
							</th>
						</tr>
					</table>
				<?php } else { ?>
								
					<table class="form-table">
						<tr>
							<th scope="row"><label>Category</label>	</th>
							<td>
								<input type="text" name="category" value="<?php echo isset($record)?$record['category']:''; ?>">
							</td>
						</tr>
						<tr>
							<th scope="row">
								<label>Image/Zip</label>
							</th>
							<td>
								<input type="file" name="file">
							</td>
						</tr>
						<tr>
							<th scope="row">
								<button>Save</button>
							</th>
						</tr>
					</table>

				<?php } ?>
				</form>
			</div>
			<?php
	}

	public function save_annotation() {
		$id = $_POST['id'];
		$areas = array();
		global $wpdb;
		if (isset($_POST['id'])) {
		    $response_data = 'Saved';
			if(isset($_POST['box'])) {
				$areas = $_POST['box'];
			}
			$sub_action = $_POST['sub_action'];

			$annotated = true;
			$trained = false;

			if (in_array($sub_action, ['save', 'save-next'])) {
				$res = $wpdb->update( $wpdb->prefix . 'deeppress',
					array(
						'box'          => json_encode( $areas ),
						'annotated'    => $annotated,
						'trained'      => $trained,
						'annotated_by' => get_current_user_id(),
						'annotated_at' => date( "Y-m-d H:i:s" )
					), array( 'id' => $_POST['id'] ) );
			}
			if($sub_action === 'delete' && current_user_can( 'manage_options' )) {
				do_action('delete_deeppress_record', $_POST['id']);
				$response_data = 'Deleted!!';
            }

			$next_row = array();
			if (in_array($sub_action, ['skip', 'save-next', 'delete'])){
			    $where = "";
			    if (key_exists('group_id', $_POST) && !empty($_POST['group_id'])) {
			        $where = "and group_id = '". $_POST['group_id'] . "'";
                }
				$next_row = $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress WHERE annotated = False $where order BY RAND() LIMIT 1", ARRAY_A );
				// $next_row = $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress WHERE annotated = False and count > 0 order BY RAND() LIMIT 1", ARRAY_A );
				$pos =  strpos($next_row['image'], "/wp-content");
				$next_row['image'] = get_site_url().substr($next_row['image'], $pos);
				$next_row['detections'] = preg_replace('/\\\\"/m', '"', $next_row['detections']);
            }

			$response = array(
				'what'=>'result',
				'action'=>'save_annotation_' . $_POST['id'],
				'id'=>$res,
				'data'=>$response_data,
                'next' => $next_row
			);
			wp_send_json($response);
		}
		wp_die();
	}

	public function process_actions() {
	    if(! isset($_REQUEST['action']) || ! isset($_REQUEST['page']))
	        return;
		$action = $_REQUEST['action'];
		$page = $_REQUEST['page'];
		//var_dump($page);
		if ( !current_user_can( 'manage_options' ) )  {
			return;
		}
		if ("delete" === $action && $page === 'deeppress') {
			if (isset($_REQUEST['id'])) {
				do_action('delete_deeppress_record', $_REQUEST['id']);
				wp_redirect( remove_query_arg( array( '_wp_http_referer', '_wpnonce', 'action', 'record' ), wp_get_referer() ) );
				exit;
			}
			if (isset($_REQUEST['record'])) {
				global $wpdb;
				// $uploadpath = wp_get_upload_dir();
				// TODO: Delete file also
				foreach ($_REQUEST['record'] as $id){
					do_action('delete_deeppress_record', $id);
				}
				if ( ! empty( $_GET['_wp_http_referer'] ) ) {
					wp_redirect( remove_query_arg( array( '_wp_http_referer', '_wpnonce', 'action', 'record' ), wp_get_referer() ) );
					exit;
				}
			}

		}
		if ("delete" === $action && $page === 'classification') {
			if (isset($_REQUEST['id'])) {
				do_action('delete_deeppress_classification_record', $_REQUEST['id']);
				wp_redirect( remove_query_arg( array( '_wp_http_referer', '_wpnonce', 'action', 'record' ), wp_get_referer() ) );
				exit;
			}
			if (isset($_REQUEST['record'])) {
				global $wpdb;
				// $uploadpath = wp_get_upload_dir();
				// TODO: Delete file also
				foreach ($_REQUEST['record'] as $id){
					do_action('delete_deeppress_classification_record', $id);
				}
				if ( ! empty( $_GET['_wp_http_referer'] ) ) {
					wp_redirect( remove_query_arg( array( '_wp_http_referer', '_wpnonce', 'action', 'record' ), wp_get_referer() ) );
					exit;
				}
			}

		}

		if ("retrain" === $action && $page === 'stats') {
			global $wpdb;

			$wpdb->update( $wpdb->prefix . "deeppress", array('trained' => false), array('trained' => true) );
			wp_redirect( menu_page_url('stats', false));
			exit;
        }
    }

    private function save_data() {
        if(isset($_REQUEST['page']) && in_array($_REQUEST['page'], array_keys($this->modules))) {
            $action = 'list';
	        if(isset($_REQUEST['action'])) {
		        $action      = $_REQUEST['action'];
	        }

	        $module_name = $_REQUEST['page'];
	        if("POST" === $_SERVER['REQUEST_METHOD']) {

	            if ( ! in_array( $action, array( 'create', 'edit' ) ) ) {
		            return;
	            }

	            $fields = $this->modules[ $module_name ]['fields'];
	            $data   = array();
	            foreach ( $fields as $k => $v ) {
		            if ( isset( $_POST[ $k ] ) ) {
			            $data[ $k ] = $_POST[ $k ];
			            if(isset($v['serialize']) && $v['serialize']) {
				            $data[ $k ] = serialize($data[ $k ] );
                        }
		            }
	            }

	            $message = '10';
	            global $wpdb;


                if(isset($data['parent']) && ($data['parent']>0)) {
                    $result = $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "dp_models WHERE id = ".$data['parent'], ARRAY_A );
                    $data['architecture'] = $result['architecture'];
                }

	            if ( isset( $_REQUEST['id'] ) ) {
		            $result = $wpdb->update( $wpdb->prefix . $_REQUEST['page'], $data, array( 'id' => $_REQUEST['id'] ) );
	                $message = '11';
	            } else {
		            $result = $wpdb->insert( $wpdb->prefix . $_REQUEST['page'], $data );
	            }

	            if ( false === $result ) {
	                $message = '12';
		            //var_dump("failed to save");
		            //exit();
	            } else {
	                $sendback = remove_query_arg('action', wp_get_referer());
		            wp_safe_redirect(add_query_arg(['message' => $message], $sendback));
                }
            }
            if ("delete" === $action) {
	            if (isset($_REQUEST['id'])) {
	                if (is_array($_REQUEST['id'])) {
	                    $ids = $_REQUEST['id'];
                    } else {
	                    $ids = array($_REQUEST['id']);
	                }
	                foreach ($ids as $id) {
	                    global $wpdb;
		                $wpdb->delete( $wpdb->prefix . $module_name, array( 'id' => $id ) );
	                }
	            }
	            if ( wp_get_referer() )
	            {
		            wp_safe_redirect( wp_get_referer() );
	            }
	            else
	            {
		            //wp_safe_redirect( get_home_url() );
                }
            }
        }
    }
}
