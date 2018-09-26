<?php 
/**
 * Plugin Name: DeepPress
 * Plugin URI: https://baseapp.com
 * Description: Deep-learning process automated. Manage models, annotate images automate training process.
 * Author: BaseApp Systems
 * Version: 1.0.1
 * Author URI: https://baseapp.com
 *
 */

// If this file is called directly, abort.
if ( ! defined( 'WPINC' ) ) {
	die;
}



$models = array(
	'ssd_mobilenet_v1_coco'                 => 'ssd_mobilenet_v1_coco',
	'ssd_mobilenet_v2_coco'                 => 'ssd_mobilenet_v2_coco',
	'ssdlite_mobilenet_v2_coco'             => 'ssdlite_mobilenet_v2_coco',
	'ssd_inception_v2_coco'                 => 'ssd_inception_v2_coco',
	'faster_rcnn_inception_v2_coco'         => 'faster_rcnn_inception_v2_coco',
	'faster_rcnn_resnet50_coco'             => 'faster_rcnn_resnet50_coco',
	'faster_rcnn_resnet50_lowproposals_coco'     => 'faster_rcnn_resnet50_lowproposals_coco',
	'rfcn_resnet101_coco'                   => 'rfcn_resnet101_coco',
	'faster_rcnn_resnet101_coco'            => 'faster_rcnn_resnet101_coco',
	'faster_rcnn_resnet101_lowproposals_coco'                       => 'faster_rcnn_resnet101_lowproposals_coco',
	'faster_rcnn_inception_resnet_v2_atrous_coco'                   => 'faster_rcnn_inception_resnet_v2_atrous_coco',
	'faster_rcnn_inception_resnet_v2_atrous_lowproposals_coco'      => 'faster_rcnn_inception_resnet_v2_atrous_lowproposals_coco',
	'faster_rcnn_nas'                       => 'faster_rcnn_nas',
	'faster_rcnn_nas_lowproposals_coco'     => 'faster_rcnn_nas_lowproposals_coco',
	'mask_rcnn_inception_resnet_v2_atrous_coco'     => 'mask_rcnn_inception_resnet_v2_atrous_coco',
	'mask_rcnn_inception_v2_coco'           => 'mask_rcnn_inception_v2_coco',
	'mask_rcnn_resnet101_atrous_coco'       => 'mask_rcnn_resnet101_atrous_coco',
	'mask_rcnn_resnet50_atrous_coco'        => 'mask_rcnn_resnet50_atrous_coco',
	'faster_rcnn_resnet101_kitti'           => 'faster_rcnn_resnet101_kitti',
	'faster_rcnn_inception_resnet_v2_atrous_oid'     => 'faster_rcnn_inception_resnet_v2_atrous_oid',
	'faster_rcnn_inception_resnet_v2_atrous_lowproposals_oid'     => 'faster_rcnn_inception_resnet_v2_atrous_lowproposals_oid',
	'faster_rcnn_resnet101_ava_v2.1'        => 'faster_rcnn_resnet101_ava_v2.1',
);

global $dp_modules;
$dp_modules = array(
	'dp_models' => array(
		'page_title' => 'Models',
		'menu_title' => 'Models',
		'menu_slug' => 'dp_models',
		'fields'    =>  array(
			'name' => [
				'name'  =>  'name',
				'type'  =>  'text',
				'placeholder'   =>  'Name',
				'value'     =>  '',
				'required'  =>  1,
			],
			'file_name' => [
				'name'  =>  'file_name',
				'type'  =>  'text',
				'placeholder'   =>  'File name',
				'value'     =>  '',
				'unique'    => 1,
				'required'  =>  1,
				'instructions'  =>  'Name of the file where new model will be saved.'
			],
			'model_type' => [
				'name'  =>  'model_type',
				'type'  =>  'select',
				'placeholder'   =>  'New Model type',
				'value'     =>  'detector',
				'choices'   => ['detector' => "Object Detector", 'classifier' => 'Image Classifier'],
				'instructions'  => 'New model type.<br>Object Detector : Detect objects in images.<br>Image Classifier: Classify images.'
			],
			'type' => [
				'name'  =>  'type',
				'type'  =>  'select',
				'placeholder'   =>  'New Model Creation type',
				'value'     =>  'new',
				'choices'   => ['new' => "New Model", 'extend' => 'Inherit from parent'],
				'instructions'  => 'Type of new model.<br>New Model : A new model will be created from zero.'
			],
			'architecture' => [
				'name'  =>  'architecture',
				'type'  =>  'select',
				'placeholder'   =>  'New Model Architecture',
				'value'     =>  '',
				'choices'           => $models,
				'instructions'  =>  'Model architecture for New Model.'
			],
			'parent' => [
				'name'  =>  'parent',
				'type'  =>  'select',
				'relative' =>  1,
				'module'    =>  'dp_models',
				'placeholder'   =>  'Parent Model',
				'value'     =>  '0',
				'choices'   => ['0' => "Base SSD Inception"],
				'instructions'  =>  'This model will be used as parent model.'
			],
			'last_trained' => [
				'name'  =>  'last_trained',
				'type'  =>  'text',
				'placeholder'   =>  'Last Trained',
				'value'     =>  '',
				'instructions'  =>  'Time the model is last trained on.'
			]
		)
	),
	'dp_groups' => array(
		'page_title' => 'Groups',
		'menu_title' => 'Groups',
		'menu_slug' => 'dp_groups',
		'fields'    =>  array(
			'name' => [
				'name'  =>  'name',
				'type'  =>  'text',
				'placeholder'   =>  'Name',
				'value'     =>  '',
				'required'  =>  1,
				'instructions' => 'Please give a name for the group'
			],
			'group_id' => [
				'name'  =>  'group_id',
				'type'  =>  'text',
				'placeholder'   =>  'Group ID',
				'value'     =>  '',
				'required'  =>  1,
			]
		)
	),
	'dp_jobs' => array(
		'page_title' => 'Jobs',
		'menu_title' => 'Jobs',
		'menu_slug' => 'dp_jobs',
		'fields'    =>  array(
			'model' => [
				'name'  =>  'model',
				'type'  =>  'select',
				'relative' =>  1,
				'module'    =>  'dp_models',
				'placeholder'   =>  'Detector Model',
				'value'     =>  '0',
				'choices'   => [],
				'instructions'  =>  'This model will be trained.'
			],
			'groups' => [
				'name'  =>  'groups',
				'type'  =>  'select',
				'relative' =>  1,
				'module'    =>  'dp_groups',
				'placeholder'   =>  'Groups',
				'value'     =>  '0',
				'choices'   => [],
				'instructions'  =>  'Group for training.',
				'multiple'  => 1,
				'foreign_key'   =>  'group_id',
				'serialize' =>  1
			],
			'steps' => [
				'name'  =>  'steps',
				'type'  =>  'number',
				'placeholder'   =>  'Steps',
				'value'     =>  50000,
				'instructions'  =>  'Number of steps to train the model.'
			],
			'status' => [
				'name'  =>  'status',
				'type'  =>  'text',
				'placeholder'   =>  'Status',
				'value' =>  'Added',
				'instructions'  => 'Current status of job'
			],
			'state' => [
				'name'  =>  'state',
				'type'  =>  'select',
				'placeholder'   =>  'Current State',
				'value'     =>  'added',
				'choices'   => ['added' => 'added', 'running' => 'running', 'paused' => 'paused'],
				'instructions'  => 'Current state of job'
			],
			'done'   =>  [
				'name'  => 'done',
				'type'  =>  'true_false',
				'value' => 0,
				'message'   => 'Job Done',
				'instructions'  => 'If it is marked as done, it will me be processed.'
			],
			'remarks' => [
				'name'  =>  'remarks',
				'type'  =>  'textarea',
				'placeholder'   =>  'Remarks',
				'value'     =>  ''
			],
		)
	),
	'dp_classes' => array(
		'page_title' => 'Classes',
		'menu_title' => 'Classes',
		'menu_slug' => 'dp_classes',
		'fields'    =>  array(
			'class' => [
				'name'  =>  'class',
				'type'  =>  'text',
				'placeholder'   =>  'Class',
				'instructions'  =>  'Unique Name of the class. eg. person, chair, computer etc.',
				'unique'    => 1,
				'value' => '',
				'required'  => 1
			],
			'weight' => [
				'name'  =>  'weight',
				'type'  =>  'number',
				'placeholder'   =>  'Weight',
				'instructions'  =>  'Weight to order in drop-down.',
				'value' => 0
			]
		)
	)
);
/**
 * Currently plugin version
 * Start at version 1.0.0 and use SemVer - https://semver.org
 * Rename this for your plugin and update it as you release new versions.
 */
define( 'DEEPPRESS_VERSION', '1.0.0' );

function activate_deeppress() {
	require_once plugin_dir_path( __FILE__ ) . 'includes/class-deeppress-activator.php';
	DeepPress_Activator::activate();
}

function deactivate_deeppress() {
	require_once plugin_dir_path( __FILE__ ) . 'includes/class-deeppress-deactivator.php';
	DeepPress_Deactivator::deactivate();
}

register_activation_hook( __FILE__, 'activate_deeppress' );
register_deactivation_hook( __FILE__, 'deactivate_deeppress' );


require plugin_dir_path( __FILE__ ) . 'includes/class-deeppress.php';

if(! function_exists('run_deeppress')){
	function run_deeppress() {
		@ini_set( 'upload_max_size' , '64M' );
		@ini_set( 'post_max_size', '64M');
		@ini_set( 'max_execution_time', '300' );
		$plugin = new DeepPress();
		$plugin->run();
	}
}
run_deeppress();


?>