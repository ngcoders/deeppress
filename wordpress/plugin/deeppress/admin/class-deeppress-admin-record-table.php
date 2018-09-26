<?php

if(!class_exists('WP_List_Table')){
	require_once( ABSPATH . 'wp-admin/includes/class-wp-list-table.php' );
}



class DeepPress_List_Table extends WP_List_Table {

	protected $table_name;
	protected $module_name;
	protected $module;

	/** ************************************************************************
	 * REQUIRED. Set up a constructor that references the parent constructor. We
	 * use the parent reference to set some default configs.
	 ***************************************************************************/


	function __construct($name, $module){
		global $status, $page, $wpdb;

		//Set parent defaults
		parent::__construct( array(
			'singular'  => $module['page_title'],     //singular name of the listed records
			'plural'    => $module['page_title'],    //plural name of the listed records
			'ajax'      => false        //does this table support ajax?
		) );

		$this->table_name = $wpdb->prefix . $name;
		$this->module_name = $name;
		$this->module = $module;
	}


	function column_default($item, $column_name){
		if (isset($this->module['fields'][$column_name]))
			return apply_filters('dp/format_value', $item[$column_name], $item['id'], $this->module['fields'][$column_name]);
		switch ($column_name) {
			default:
				return $item[$column_name];
		}

	}


	/** ************************************************************************
	 * REQUIRED if displaying checkboxes or using bulk actions! The 'cb' column
	 * is given special treatment when columns are processed. It ALWAYS needs to
	 * have it's own method.
	 *
	 * @see WP_List_Table::::single_row_columns()
	 * @param array $item A singular item (one full row's worth of data)
	 * @return string Text to be placed inside the column <td> (movie title only)
	 **************************************************************************/
	function column_cb($item){
		return sprintf(
			'<input type="checkbox" name="id[]" value="%s" />',
			 $item['id']                //The value of the checkbox should be the record's id
		);
	}

	function column_id($item) {
		//Build row actions
		$actions = array(
			'edit'      => sprintf('<a href="?page=%s&action=%s&id=%s">Edit</a>',$_REQUEST['page'],'edit',$item['id']),
			'delete'    => sprintf('<a href="?page=%s&action=%s&id=%s">Delete</a>',$_REQUEST['page'],'delete',$item['id']),
		);

		//Return the title contents
		return sprintf('%1$s %2$s',
			$item['id'],
			$this->row_actions($actions)
		);
	}

	function get_columns(){
		$columns = array(
			'cb'                => '<input type="checkbox" />', //Render a checkbox instead of text
			'id'                => 'ID'
		);
		foreach ($this->module['fields'] as $f) {
			$columns[$f['name']] = isset($f['placeholder']) ? $f['placeholder'] : $f['name'];
		}

		$columns['created_at'] = 'Created At';

		// Add more columns

		return $columns;
	}


	/** ************************************************************************
	 * Optional. If you want one or more columns to be sortable (ASC/DESC toggle),
	 * you will need to register it here. This should return an array where the
	 * key is the column that needs to be sortable, and the value is db column to
	 * sort by. Often, the key and value will be the same, but this is not always
	 * the case (as the value is a column name from the database, not the list table).
	 *
	 * This method merely defines which columns should be sortable and makes them
	 * clickable - it does not handle the actual sorting. You still need to detect
	 * the ORDERBY and ORDER querystring variables within prepare_items() and sort
	 * your data accordingly (usually by modifying your query).
	 *
	 * @return array An associative array containing all the columns that should be sortable: 'slugs'=>array('data_values',bool)
	 **************************************************************************/
	function get_sortable_columns() {
		$sortable_columns = array(
			'id'  => array('id',true),
			'created_at'  => array('created_at',true)
		);
		return $sortable_columns;
	}

	function get_bulk_actions() {
		$actions = array(
			'delete'    => 'Delete'
		);
		return $actions;
	}


	/** ************************************************************************
	 * Optional. You can handle your bulk actions anywhere or anyhow you prefer.
	 * For this example package, we will handle it in the class to keep things
	 * clean and organized.
	 *
	 * @see $this->prepare_items()
	 **************************************************************************/
	function process_bulk_action() {

		//Detect when a bulk action is being triggered...
		if( 'delete'===$this->current_action() ) {
		}

	}

	protected function extra_tablenav( $which ) {
		if ($which !== 'top')
			return;
	}


	/** ************************************************************************
	 * REQUIRED! This is where you prepare your data for display. This method will
	 * usually be used to query the database, sort and filter the data, and generally
	 * get it ready to be displayed. At a minimum, we should set $this->items and
	 * $this->set_pagination_args(), although the following properties and methods
	 * are frequently interacted with here...
	 *
	 * @global WPDB $wpdb
	 * @uses $this->_column_headers
	 * @uses $this->items
	 * @uses $this->get_columns()
	 * @uses $this->get_sortable_columns()
	 * @uses $this->get_pagenum()
	 * @uses $this->set_pagination_args()
	 **************************************************************************/
	function prepare_items() {
		global $wpdb;

		$per_page = 10;

		$columns = $this->get_columns();
		$hidden = array();
		$sortable = $this->get_sortable_columns();

		$this->_column_headers = array($columns, $hidden, $sortable);


		/**
		 * Optional. You can handle your bulk actions however you see fit. In this
		 * case, we'll handle them within our package just to keep things clean.
		 */
		$this->process_bulk_action();



		$orderby = (!empty($_REQUEST['orderby'])) ? $_REQUEST['orderby'] : 'created_at'; //If no sort, default to title
		$order = (!empty($_REQUEST['order'])) ? $_REQUEST['order'] : 'desc'; //If no order, default to asc

		$current_page = $this->get_pagenum();

		$table_name = $this->table_name;


		/**
		 * The WP_List_Table class does not handle pagination for us, so we need
		 * to ensure that the data is trimmed to only the current page. We can use
		 * array_slice() to
		 */
		$where = array();
		if (isset($_REQUEST['start_time']) && $_REQUEST['start_time'] !== "") {
			$where[] = "created_at >= '".$_REQUEST['start_time']."'";
		}
		if (isset($_REQUEST['end_time']) && $_REQUEST['end_time'] !== "") {
			$where[] = "created_at <= '".$_REQUEST['end_time']."'";
		}

		$where_cmd = "";
		if (sizeof($where) > 0) {
			$where_cmd = "WHERE ". implode(" AND ", $where);
		}

		$total_items = $wpdb->get_var( "SELECT COUNT(*) FROM $table_name $where_cmd" );
		//$data = array_slice($data,(($current_page-1)*$per_page),$per_page);
		$data = $wpdb->get_results(
			"
                                    SELECT * 
                                    FROM $table_name
                                    $where_cmd
                                    ORDER BY $orderby $order
                                    LIMIT $per_page OFFSET " . ($current_page-1)*$per_page,
			ARRAY_A
		);

		$this->items = $data;

		$this->set_pagination_args( array(
			'total_items' => $total_items,
			'per_page'    => $per_page,
			'total_pages' => ceil($total_items/$per_page)
		) );
	}


}

?>
