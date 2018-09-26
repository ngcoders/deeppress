<?php

class dp_field_number extends dp_field
{
	
	/*
	*  __construct
	*
	*  Set name / label needed for actions / filters
	*
	*  @since	3.6
	*  @date	23/01/13
	*/
	
	function __construct()
	{
		// vars
		$this->name = 'number';
		$this->label = __("Number",'ba');
		$this->defaults = array(
			'default_value'	=>	'',
			'min'			=>	'',
			'max'			=>	'',
			'step'			=>	'',
			'placeholder'	=>	'',
			'prepend'		=>	'',
			'append'		=>	''
		);
		
		
		// do not delete!
    	parent::__construct();
	}
		
	
	/*
	*  create_field()
	*
	*  Create the HTML interface for your field
	*
	*  @param	$field - an array holding all the field's data
	*
	*  @type	action
	*  @since	3.6
	*  @date	23/01/13
	*/
	
	function create_field( $field )
	{
		// vars
		$o = array( 'id', 'class', 'min', 'max', 'step', 'name', 'value', 'placeholder' );
		$e = '';
		
		
		// step
		if( !$field['step'] )
		{
			$field['step'] = 'any';
		}
		
		// prepend
		if( $field['prepend'] !== "" )
		{
			$field['class'] .= ' ba-is-prepended';
			$e .= '<div class="ba-input-prepend">' . $field['prepend'] . '</div>';
		}
		
		
		// append
		if( $field['append'] !== "" )
		{
			$field['class'] .= ' ba-is-appended';
			$e .= '<div class="ba-input-append">' . $field['append'] . '</div>';
		}
		
		
		$e .= '<div class="ba-input-wrap">';
		$e .= '<input type="number"';
		
		foreach( $o as $k )
		{
			$e .= ' ' . $k . '="' . esc_attr( $field[ $k ] ) . '"';	
		}
		
		$e .= ' />';
		$e .= '</div>';
		
		
		// return
		echo $e;
		
	}
	
	
	/*
	*  create_options()
	*
	*  Create extra options for your field. This is rendered when editing a field.
	*  The value of $field['name'] can be used (like bellow) to save extra data to the $field
	*
	*  @type	action
	*  @since	3.6
	*  @date	23/01/13
	*
	*  @param	$field	- an array holding all the field's data
	*/
	
	function create_options( $field )
	{
		// vars
		$key = $field['name'];
		
		?>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Default Value",'ba'); ?></label>
		<p><?php _e("Appears when creating a new post",'ba') ?></p>
	</td>
	<td>
		<?php
		
		do_action('dp/create_field', array(
			'type'	=>	'number',
			'name'	=>	'fields['.$key.'][default_value]',
			'value'	=>	$field['default_value'],
		));

		?>
	</td>
</tr>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Placeholder Text",'ba'); ?></label>
		<p><?php _e("Appears within the input",'ba') ?></p>
	</td>
	<td>
		<?php 
		do_action('dp/create_field', array(
			'type'	=>	'text',
			'name'	=>	'fields[' .$key.'][placeholder]',
			'value'	=>	$field['placeholder'],
		));
		?>
	</td>
</tr>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Prepend",'ba'); ?></label>
		<p><?php _e("Appears before the input",'ba') ?></p>
	</td>
	<td>
		<?php 
		do_action('dp/create_field', array(
			'type'	=>	'text',
			'name'	=>	'fields[' .$key.'][prepend]',
			'value'	=>	$field['prepend'],
		));
		?>
	</td>
</tr>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Append",'ba'); ?></label>
		<p><?php _e("Appears after the input",'ba') ?></p>
	</td>
	<td>
		<?php 
		do_action('dp/create_field', array(
			'type'	=>	'text',
			'name'	=>	'fields[' .$key.'][append]',
			'value'	=>	$field['append'],
		));
		?>
	</td>
</tr>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Minimum Value",'ba'); ?></label>
	</td>
	<td>
		<?php
		
		do_action('dp/create_field', array(
			'type'	=>	'number',
			'name'	=>	'fields['.$key.'][min]',
			'value'	=>	$field['min'],
		));

		?>
	</td>
</tr>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Maximum Value",'ba'); ?></label>
	</td>
	<td>
		<?php
		
		do_action('dp/create_field', array(
			'type'	=>	'number',
			'name'	=>	'fields['.$key.'][max]',
			'value'	=>	$field['max'],
		));

		?>
	</td>
</tr>
<tr class="field_option field_option_<?php echo $this->name; ?>">
	<td class="label">
		<label><?php _e("Step Size",'ba'); ?></label>
	</td>
	<td>
		<?php
		
		do_action('dp/create_field', array(
			'type'	=>	'number',
			'name'	=>	'fields['.$key.'][step]',
			'value'	=>	$field['step'],
		));

		?>
	</td>
</tr>
		<?php
	}
	
	
	/*
	*  update_value()
	*
	*  This filter is appied to the $value before it is updated in the db
	*
	*  @type	filter
	*  @since	3.6
	*  @date	23/01/13
	*
	*  @param	$value - the value which will be saved in the database
	*  @param	$field - the field array holding all the field options
	*  @param	$post_id - the $post_id of which the value will be saved
	*
	*  @return	$value - the modified value
	*/
	
	function update_value( $value, $post_id, $field )
	{
		// no formatting needed for empty value
		if( empty($value) ) {
			
			return $value;
			
		}
		
		
		// remove ','
		$value = str_replace(',', '', $value);
		
		
		// convert to float. This removes any chars
		$value = floatval( $value );
		
		
		// convert back to string. This alows decimals to save
		$value = (string) $value;
		
		
		return $value;
	}
	
	
}

new dp_field_number();

?>