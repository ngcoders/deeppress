<?php

if(!class_exists('WP_List_Table')){
    require_once( ABSPATH . 'wp-admin/includes/class-wp-list-table.php' );
}


class DeepPress_Classification_Table extends WP_List_Table {
    
    protected $table_name;
    
    /** ************************************************************************
     * REQUIRED. Set up a constructor that references the parent constructor. We 
     * use the parent reference to set some default configs.
     ***************************************************************************/

    
    function __construct(){
        global $status, $page, $wpdb;
                
        //Set parent defaults
        parent::__construct( array(
            'singular'  => 'record',     //singular name of the listed records
            'plural'    => 'records',    //plural name of the listed records
            'ajax'      => false        //does this table support ajax?
        ) );
        
        $this->table_name = $wpdb->prefix . "deeppress_classification";
        $this->per_page = 10;
    }


    function column_default($item, $column_name){
        switch ($column_name) {
            case 'id':
                $actions = array();
                if (current_user_can( 'manage_options' ))
                    $actions['delete'] = sprintf('<a href="?page=%s&action=%s&id=%s">Delete</a>',$_REQUEST['page'],'delete',$item['id']);
        
                        //Return the title contents
                return sprintf('%1$s %2$s',
                    /*$1%s*/ $item['id'],
                    /*$3%s*/ $this->row_actions($actions)
                );
                break;            
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
            '<input type="checkbox" name="%1$s[]" value="%2$s" />',
            /*$1%s*/ $this->_args['singular'],  //Let's simply repurpose the table's singular label ("movie")
            /*$2%s*/ $item['id']                //The value of the checkbox should be the record's id
        );
    }

    public function listFolderFiles($dir){
        if(is_null($dir)){
            return 0;
        }
        $ffs = scandir($dir);
        $total = 0;
        unset($ffs[array_search('.', $ffs, true)]);
        unset($ffs[array_search('..', $ffs, true)]);
    
        // prevent empty ordered elements
        if (count($ffs) < 1)
            return;
    
        // echo '<ol>';
        foreach($ffs as $ff){
            // echo '<li>'.$ff;
            if(is_dir($dir.'/'.$ff)) 
                $total += $this->listFolderFiles($dir.'/'.$ff);
            else
                $total ++;
        }
        // echo '</ol>';
        return $total;
    }
    
    

    function column_images_count($item) {
        $path = $item['dir_path'];
        return $this->listFolderFiles($path);
    }


    /** ************************************************************************
     * REQUIRED! This method dictates the table's columns and titles. This should
     * return an array where the key is the column slug (and class) and the value 
     * is the column's title text. If you need a checkbox for bulk actions, refer
     * to the $columns array below.
     * 
     * The 'cb' column is treated differently than the rest. If including a checkbox
     * column in your table you must create a column_cb() method. If you don't need
     * bulk actions or checkboxes, simply leave the 'cb' entry out of your array.
     * 
     * @see WP_List_Table::::single_row_columns()
     * @return array An associative array containing column information: 'slugs'=>'Visible Titles'
     **************************************************************************/
    function get_columns(){
        $columns = array(
            'cb'                => '<input type="checkbox" />', //Render a checkbox instead of text
            'id'                => 'Id',
            'category'         => 'Category',
            'dir_path'             => 'Path',
            'images_count'      => 'Total Images',
            'created_at'        => 'Created At',
            'updated_at'        => 'Updated At'
        );
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
            'created_at'    => array('created_at',true),
            'updated_at'    => array('updated_at',false),
            'category'    => array('category',false),
            'id'  => array('id',false)
        );
        return $sortable_columns;
    }

    function get_bulk_actions() {
	    $actions = array();
        if (current_user_can( 'manage_options' ))
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
	    
    }

    protected function extra_tablenav( $which ) {
        if ($which !== 'top')
            return;
        global $wpdb;
        $table = $this->table_name;
        $categories = $wpdb->get_results(
            "
            SELECT DISTINCT      category as name, category as category_name
            FROM        $this->table_name 
            ORDER BY    category desc
            LIMIT 100
            ",
	        ARRAY_A
        );
	    add_thickbox();

	    ?>
            <div class="alignleft actions">
                <label for="group_id" class="alignleft actions">Categories: </label>
                <select name="category_name">
                    <option value="all">All Categories</option>
                    <?php 
                        foreach ($categories as $category) {
                            $id = $category['category_name'];
                            $name = $category['name'];
                            if (trim($id) == "" || is_null($id))
                                continue;
                            $selected = $_REQUEST['category_name'] == $id ? "selected" : "";
                            echo "<option $selected value='$id'>$name </option>";
                        }
                    ?>
                </select>
                
        <?php
                submit_button('Filter', '', 'filter_action', false);
        ?>
            </div>

        <?php         
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
        $_SERVER['REQUEST_URI'] = remove_query_arg( '_wp_http_referer', $_SERVER['REQUEST_URI'] );
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
        if (isset($_REQUEST['category_name']) && $_REQUEST['category_name'] !== "all") {
            $where[] = "category = '".$_REQUEST['category_name']."'";
        }
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
