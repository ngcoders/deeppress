<?php
/**
 * Created by PhpStorm.
 * User: gopal
 * Date: 5/7/18
 * Time: 10:16 AM
 */

class dp_basic_functions
{

	/*
	*  __construct
	*
	*  @description:
	*  @since 3.1.8
	*  @created: 23/06/12
	*/

	function __construct()
	{
        add_action('delete_deeppress_record', array($this, 'delete_record'), 5, 1);
        add_action('delete_deeppress_classification_record', array($this, 'delete_classification_record'), 5, 1);
        add_filter('get_deeppress_record', array($this, 'get_record'), 5, 1);
        add_filter('get_classification_record', array($this, 'get_classification_record'), 5, 1);
		add_filter('get_deeppress_group_last_record', array($this, 'get_group_last_record'), 5, 1);
        add_filter('dp_show_deeppress_stats', array($this, 'deeppress_stats'), 5, 1);

        add_filter('dp_images_in_dir', array($this, 'dp_images_in_dir'), 5, 1);
    }
    
    public function dp_images_in_dir($dir) {
        $ffs = scandir($dir);
        $all = [];
        unset($ffs[array_search('.', $ffs, true)]);
        unset($ffs[array_search('..', $ffs, true)]);
    
        // prevent empty ordered elements
        if (count($ffs) < 1)
            return $all;
    
        foreach($ffs as $ff){
            $file_path = $dir.'/'.$ff; 
            if(is_dir($file_path)) {
                $all = array_merge($all, apply_filters('dp_images_in_dir', $file_path)) ;   
            } else {
                $ext = pathinfo($file_path, PATHINFO_EXTENSION);
                if(in_array(strtolower($ext) , ['jpeg', 'jpg', 'png']))
                    $all[] = $file_path;
            }
        }
        // echo '</ol>';
        return $all;
    }

	function get_record($id)
    {
	    global $wpdb;
	    return $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress WHERE id = $id", ARRAY_A );
    }

    function get_classification_record($id)
    {
	    global $wpdb;
	    return $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress_classification WHERE id = $id", ARRAY_A );
    }

	function get_group_last_record($id)
	{
		global $wpdb;
		return $wpdb->get_row( "SELECT * FROM ". $wpdb->prefix . "deeppress WHERE group_id = '$id' order by created_at desc limit 1", ARRAY_A );
	}


	/*
	*  delete_record
	*
	*  @description: delete a deeppress record from the db
	*  @since: 1.0
	*/

	function delete_record($id)
	{
		global $wpdb;
		// $uploadpath = wp_get_upload_dir();
		$record = apply_filters('get_deeppress_record', $id);
		@unlink($record['image_file']);
		@unlink($record['processed_image_file']);
		$wpdb->delete( $wpdb->prefix . "deeppress", array( 'id' => $id ) );
    }

    function rrmdir($dir) { 
        if (is_dir($dir)) { 
          $objects = scandir($dir); 
          foreach ($objects as $object) { 
            if ($object != "." && $object != "..") { 
              if (is_dir($dir."/".$object))
                $this->rrmdir($dir."/".$object);
              else
                unlink($dir."/".$object); 
            } 
          }
          rmdir($dir); 
        } 
      }
    
    function delete_classification_record($id){
        global $wpdb;
        $record = apply_filters('get_classification_record', $id);
        if ( $record['dir_path'] && strpos($record['dir_path'], 'uploads') < strpos($record['dir_path'], $record['category'])) {
            $this->rrmdir($record['dir_path']);
        }
        $wpdb->delete( $wpdb->prefix . "deeppress_classification", array( 'id' => $id ) );
        
    }

	function deeppress_stats()
    {
	    global $wpdb;
	    $table_name = $wpdb->prefix . "deeppress";
	    $to_train = $wpdb->get_var("SELECT count(id) FROM $table_name  WHERE annotated = True AND trained= False");
	    $all_annotated = $wpdb->get_var("SELECT count(id) FROM  $table_name  WHERE annotated = True");
	    $all_trained = $wpdb->get_var("SELECT count(id) FROM  $table_name  WHERE annotated = True AND trained= True");

	    $annotators = $wpdb->get_results(
		    "
                                    SELECT count(id) as count, annotated_by
                                    FROM $table_name
                                    WHERE annotated = True
                                    GROUP BY annotated_by
                                    ORDER BY count desc
                                    LIMIT 10",
		    ARRAY_A
	    );

	    $daily_annotated = $wpdb->get_results(
		    "
                                    SELECT count(id) as count, DATE(annotated_at) as annotated_at
                                    FROM $table_name
                                    WHERE annotated = True
                                    GROUP BY DATE(annotated_at)
                                    ORDER BY annotated_at desc
                                    LIMIT 10",
		    ARRAY_A
	    );

	    $daily_stats = $wpdb->get_results(
		    "
                                    SELECT count(id) as count, DATE(created_at) as created_at
                                    FROM $table_name
                                    GROUP BY DATE(created_at)
                                    ORDER BY created_at desc
                                    LIMIT 10",
		    ARRAY_A
	    );


       ?>
        <div id="dashboard-widgets" class="metabox-holder">
            <div class="postbox-container">
                <div class="meta-box-sortables">
                    <div class="postbox " >
                        <h2 class='hndle'><span>At a Glance</span></h2>
                        <div class="inside">
                            <div class="main">
                                <table class="wp-list-table widefat">
                                    <tr><td>Annotated</td><td><?php echo $to_train ?></td></tr>
                                    <tr><td>All Annotated</td><td><?php echo $all_annotated ?></td></tr>
                                    <tr>
                                        <td>All Trained
                                            <?php if($all_trained > 0) { ?>
                                                <br> <a href="<?php menu_page_url('stats') ?>&action=retrain" title="Use again for training">Train again</a>
                                            <?php } ?>
                                        </td>
                                        <td><?php echo $all_trained ?></td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="postbox-container">
                <div class="meta-box-sortables">
                    <div class="postbox " >
                        <h2 class='hndle'><span>Top Annotator</span></h2>
                        <div class="inside">
                            <div class="main">
                                <table class="wp-list-table widefat">
                                    <?php foreach ($annotators as $annotator) { ?>
                                    <tr><td><?php
                                        if ($annotator['annotated_by'] == 0) {
                                            echo 'Unknown';
                                        } else {
                                            $user = get_user_by('id', $annotator['annotated_by']);
                                            echo $user->display_name;
                                        }
		                                    echo " </td><td> ";
                                        echo $annotator['count'] ?>
                                        </td></tr>
                                    <?php } ?>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="postbox-container">
                <div class="meta-box-sortables">
                    <div class="postbox " >
                        <h2 class='hndle'><span>Daily Annotations</span></h2>
                        <div class="inside">
                            <div class="main">
                                <table class="wp-list-table widefat">
	                                <?php foreach ($daily_annotated as $st) { ?>
                                        <tr><td><?php
			                                echo $st['annotated_at'] ;
			                                echo " </td><td> ";
			                                echo $st['count'] ;

                                                ?></td></tr>
	                                <?php } ?>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="postbox-container">
                <div class="meta-box-sortables">
                    <div class="postbox " >
                        <h2 class='hndle'><span>Daily Images Captured</span></h2>
                        <div class="inside">
                            <div class="main">
                                <table class="wp-list-table widefat">
                                    <?php foreach ($daily_stats as $st) { ?>
                                        <tr><td><?php
                                            echo $st['created_at'] ;
                                            echo "</td><td>";
                                            echo $st['count'] ;

                                            ?></td></tr>
                                    <?php } ?>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <?php
    }
}

new dp_basic_functions();

?>